import json
import re
import os
from google import genai
from google.genai import types
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import Conversation, Message, KnowledgeBase

# Initialize Gemini client
client = None
if settings.GOOGLE_API_KEY:
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

def home(request):
    return render(request, 'chatbot/home.html')

@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not user_message:
            return JsonResponse({'error': 'Empty message'}, status=400)
        
        # Get or create conversation
        if conversation_id:
            conversation = get_object_or_404(Conversation, id=conversation_id)
        else:
            conversation = Conversation.objects.create(
                title=user_message[:50] + "...",
                session_key=request.session.session_key or "anonymous"
            )
        
        # Save user message
        Message.objects.create(
            conversation=conversation,
            content=user_message,
            is_user=True
        )
        
        # Get bot response
        bot_response = generate_gemini_response(user_message, conversation)
        
        # Save bot message
        bot_message = Message.objects.create(
            conversation=conversation,
            content=bot_response,
            is_user=False
        )
        
        # Update conversation title
        if conversation.messages.count() == 2:
            conversation.title = generate_conversation_title(user_message)
            conversation.save()
        
        return JsonResponse({
            'response': bot_response,
            'conversation_id': conversation.id,
            'message_id': bot_message.id,
            'timestamp': bot_message.timestamp.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def generate_gemini_response(user_message, conversation):
    """Generate response using Google Gemini with the new SDK"""
    
    # First, check knowledge base
    kb_response = check_knowledge_base(user_message)
    if kb_response:
        return kb_response
    
    # Check if Gemini client is configured
    if not client:
        return generate_fallback_response(user_message)
    
    try:
        # Get conversation history for context
        recent_messages = conversation.messages.order_by('-timestamp')[:6]
        
        # Build conversation history
        conversation_history = []
        for msg in reversed(recent_messages):
            role = "user" if msg.is_user else "assistant"
            conversation_history.append(f"{role}: {msg.content}")
        
        # Enhanced system instruction with formatting guidance
        system_instruction = """You are EduBot, a helpful and friendly university assistant. Your role is to assist students with:

**COURSES & ACADEMICS:**
- Course information, prerequisites, schedules
- Professor details, office hours  
- Department contacts and resources

**DEADLINES & SCHEDULES:**
- Registration dates, add/drop deadlines
- Exam schedules, assignment due dates
- Academic calendar events

**CAMPUS RESOURCES:**
- Library hours, tutoring centers, study spaces
- IT support, health services, counseling
- Career services, internships, job opportunities

**GUIDANCE & SUPPORT:**
- Study tips, time management strategies
- Campus life, student organizations
- University policies and procedures

**RESPONSE STYLE:**
- Use **bold** for important terms and headings
- Use bullet points with • for lists
- Use numbered lists for steps or sequences
- Keep responses clear and well-structured
- Be concise but thorough

If unsure about specific information, suggest checking official sources. Keep responses under 300 words."""

        # Build the full content
        history_text = "\n".join(conversation_history) if conversation_history else "No previous messages"
        
        full_content = f"""System: {system_instruction}

Conversation History:
{history_text}

Current User Question: {user_message}

Please provide a helpful, formatted response:"""

        # Generate response using Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_content,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=500,
                top_p=0.8,
                top_k=40
            )
        )
        
        return response.text
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        return generate_fallback_response(user_message)
    
def generate_fallback_response(user_message):
    """Intelligent fallback responses with formatting"""
    user_lower = user_message.lower()
    
    fallback_patterns = {
        r'\b(directions?|location|where is|how to get to|how do i get to|route|map)\b': [
            "**Okay! To give you directions, I need to know:**\n\n1. **Where are you starting from?** (e.g., Faculty of Engineering, Library, Main Gate)\n2. **Where are you trying to go?** (e.g., specific building, department, landmark)\n\nOnce I have that information, I can provide you with the best route. If you're unsure of building names, you can check the university's website for a campus map.",
            "**I can help with directions!** Please tell me:\n\n• **Your starting location** on campus\n• **Your destination** \n\nWith these details, I'll give you clear directions around campus.",
        ],
        r'\b(hello|hi|hey|greetings)\b': [
            "**Hello!** I'm EduBot, your university assistant. How can I help you with **courses, deadlines, or campus resources** today?",
            "**Hi there!** I'm here to assist with university matters. What can I help you with?",
        ],
        r'\b(course|class|subject)\b': [
            "**I can help with course information!** Which specific **course or department** are you interested in?",
            "**For course details**, check the university catalog or let me know which **specific course** you're asking about.",
        ],
        r'\b(deadline|due|when is|due date)\b': [
            "**Important deadlines** are usually found in:\n\n• **Academic calendar**\n• **Course syllabus** \n• **University website**\n\nWhich specific deadline are you looking for?",
            "**Deadline information** is available in your **course materials** and the **official academic calendar**. What specific deadline do you need help with?",
        ],
        r'\b(study|learn|exam|test)\b': [
            "**For academic success**, try these strategies:\n\n• **Review regularly** and don't cram\n• **Practice actively** with past papers\n• **Use campus resources** like the tutoring center\n• **Form study groups** with classmates",
            "**Effective studying** involves:\n\n1. **Good time management**\n2. **Active learning techniques**\n3. **Utilizing campus support services**\n4. **Regular breaks** and self-care",
        ],
    }
    
    # Check for matching patterns
    for pattern, responses in fallback_patterns.items():
        if re.search(pattern, user_lower):
            import random
            return random.choice(responses)
    
    # Default intelligent response with formatting
    default_responses = [
        f"**I'd be happy to help with '{user_message}'!**\n\nAs a university assistant, I specialize in:\n\n• **Course information** and prerequisites\n• **Academic deadlines** and schedules\n• **Campus resources** and services\n• **General student guidance**\n\nCould you provide more specific details about what you need?",
        f"**That's an interesting question about '{user_message}'!**\n\nI'm here to help with **university-related topics** including:\n\n• Course details and schedules\n• Campus facilities and resources\n• Academic planning and deadlines\n• Student support services\n\nWhat specific information can I help you find?",
    ]
    import random
    return random.choice(default_responses)

def check_knowledge_base(user_message):
    """Check if question matches known patterns in knowledge base"""
    user_lower = user_message.lower()
    
    # Check for course codes
    course_match = re.search(r'[a-z]{2,4}\s?\d{3,4}', user_lower)
    if course_match:
        course_code = course_match.group().upper()
        return f"I see you're asking about {course_code}. For detailed course information including prerequisites, professor details, and schedule, please check the official university course catalog or contact the department directly."
    
    # Check knowledge base entries
    knowledge_entries = KnowledgeBase.objects.all()
    for entry in knowledge_entries:
        keywords = [kw.strip().lower() for kw in entry.keywords.split(',')]
        if any(keyword in user_lower for keyword in keywords):
            return entry.answer
    
    return None

def generate_conversation_title(first_message):
    """Generate a title for the conversation"""
    if len(first_message) > 47:
        return first_message[:47] + "..."
    return first_message

@require_http_methods(["GET"])
def conversation_history(request, conversation_id):
    """Get conversation history"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    messages = conversation.messages.all()
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'is_user': msg.is_user,
            'timestamp': msg.timestamp.isoformat()
        })
    
    return JsonResponse({
        'conversation_id': conversation.id,
        'title': conversation.title,
        'messages': messages_data
    })

@require_http_methods(["GET"])
def list_conversations(request):
    """List all conversations for the session"""
    conversations = Conversation.objects.filter(
        session_key=request.session.session_key
    ).order_by('-updated_at')
    
    conversations_data = []
    for conv in conversations:
        conversations_data.append({
            'id': conv.id,
            'title': conv.title,
            'updated_at': conv.updated_at.isoformat(),
            'message_count': conv.messages.count()
        })
    
    return JsonResponse({'conversations': conversations_data})