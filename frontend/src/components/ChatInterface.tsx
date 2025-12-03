/**
 * Chat Interface Component
 * Allows providers to ask follow-up questions about patient data
 */
import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Paper,
  Chip,
  Alert,
} from '@mui/material';
import { Send, QuestionAnswer } from '@mui/icons-material';
import { apiService } from '../services/api';
import { ChatMessage, FHIRSource } from '../types';

interface ChatInterfaceProps {
  patientId: string;
  patientName: string;
  fhirSource?: FHIRSource;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ patientId, patientName, fhirSource }) => {
  const [question, setQuestion] = useState('');
  const [conversation, setConversation] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const suggestedQuestions = [
    "What was the patient's last A1C value?",
    "Any recent medication changes?",
    "Summarize cardiovascular history",
    "Are there any drug interactions to watch for?",
  ];

  const handleAskQuestion = async () => {
    if (!question.trim()) return;

    try {
      setLoading(true);
      setError(null);

      const response = await apiService.askQuestion(patientId, question, conversation, fhirSource);

      setConversation(response.conversation_history);
      setQuestion('');
    } catch (err: any) {
      setError(err.message || 'Failed to get answer');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAskQuestion();
    }
  };

  const handleSuggestedQuestion = (suggested: string) => {
    setQuestion(suggested);
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <QuestionAnswer color="primary" />
          <Typography variant="h6">Ask Questions About {patientName}</Typography>
        </Box>

        {error && (
          <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Suggested Questions */}
        {conversation.length === 0 && (
          <Box mb={2}>
            <Typography variant="body2" color="text.secondary" mb={1}>
              Try asking:
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {suggestedQuestions.map((suggested, idx) => (
                <Chip
                  key={idx}
                  label={suggested}
                  onClick={() => handleSuggestedQuestion(suggested)}
                  size="small"
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>
        )}

        {/* Conversation History */}
        {conversation.length > 0 && (
          <Box mb={2} maxHeight={400} sx={{ overflowY: 'auto' }}>
            {conversation.map((message, idx) => (
              <Paper
                key={idx}
                elevation={0}
                sx={{
                  p: 2,
                  mb: 1,
                  bgcolor: message.role === 'user' ? 'primary.50' : 'grey.50',
                  ml: message.role === 'user' ? 4 : 0,
                  mr: message.role === 'user' ? 0 : 4,
                }}
              >
                <Typography variant="caption" color="text.secondary" fontWeight="bold">
                  {message.role === 'user' ? 'You' : 'AI Assistant'}
                </Typography>
                <Typography variant="body2" whiteSpace="pre-wrap">
                  {message.content}
                </Typography>
              </Paper>
            ))}
          </Box>
        )}

        {/* Input Field */}
        <Box display="flex" gap={1}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            placeholder="Ask a question about this patient..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
          />
          <Button
            variant="contained"
            onClick={handleAskQuestion}
            disabled={loading || !question.trim()}
            startIcon={loading ? <CircularProgress size={20} /> : <Send />}
            sx={{ minWidth: 100 }}
          >
            Ask
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

