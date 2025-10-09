from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_user = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    tokens_used = models.IntegerField(default=0)

    class Meta:
        ordering = ['timestamp']

class KnowledgeBase(models.Model):
    QUESTION_TYPES = [
        ('course', 'Course Information'),
        ('deadline', 'Deadlines'),
        ('resource', 'Campus Resources'),
        ('general', 'General Information'),
    ]
    
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    question_pattern = models.CharField(max_length=500)
    answer = models.TextField()
    keywords = models.CharField(max_length=500, help_text="Comma-separated keywords")
    
    def __str__(self):
        return self.question_pattern