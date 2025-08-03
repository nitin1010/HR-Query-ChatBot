# HR Resource Query Chatbot

An AI-powered HR assistant that helps find employees using natural language queries. Built with RAG (Retrieval-Augmented Generation) using Mistral LLM, sentence transformers, FastAPI, and Streamlit.

## 🎯 Overview

This chatbot allows HR teams to find employees naturally by asking questions like:
- "Find Python developers with 3+ years experience"
- "Who has worked on healthcare projects?"  
- "Suggest people for a React Native project"
- "Find developers who know both AWS and Docker"

The system uses a RAG architecture combining semantic search with AI-generated responses for intelligent employee matching.

## ✨ Features

- **Natural Language Queries**: Ask questions in plain English
- **Semantic Search**: Uses sentence transformers for intelligent matching
- **AI-Generated Responses**: Mistral LLM provides conversational responses
- **Advanced Filtering**: Search by skills, experience, department, availability
- **Real-time Chat Interface**: Streamlit-based interactive UI
- **REST API**: FastAPI backend with automatic documentation
- **Employee Analytics**: Statistics and insights about your workforce

## 🏗 Architecture

```
Frontend (Streamlit) ↔ FastAPI Backend ↔ RAG System
                                           ├── Embeddings (all-MiniLM-L6-v2)
                                           ├── Vector Search (Cosine Similarity)
                                           └── Generation (Mistral-7B)
```

### Components:
- **Retrieval**: Sentence transformers create embeddings for semantic search
- **Augmentation**: Combines query with relevant employee data
- **Generation**: Mistral LLM generates natural language responses
- **Backend**: FastAPI serves endpoints for chat and search
- **Frontend**: Streamlit provides interactive chat interface

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- At least 8GB RAM (16GB recommended for Mistral)
- CUDA GPU optional (for faster inference)

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd hr-chatbot
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Model Directory
```bash
mkdir models
```

### 5. Configure Environment
Copy `.env` file and adjust settings if needed:
- Set `USE_CUDA=false` if no GPU available
- Adjust `MODEL_PATH` if needed

### 6. Start the API Server
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Launch Streamlit Interface
In a new terminal:
```bash
streamlit run frontend/streamlit_app.py
```

### 8. Access the Application
- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs

## 📚 API Documentation

### Endpoints

#### POST /chat
Process natural language HR queries
```json
{
  "query": "Find Python developers with 3+ years experience",
  "top_k": 5
}
```

#### GET /employees/search
Search employees with filters
```
GET /employees/search?skills=Python,React&min_experience=3&availability=available
```

#### GET /employees
Get all employees

#### GET /employees/{id}
Get specific employee

#### GET /employees/stats
Get employee statistics

#### GET /health
Health check endpoint

## 🤖 AI Development Process

### AI Tools Used
- **GitHub Copilot**: Code completion and suggestion (~30% of code)
- **Claude/ChatGPT**: Architecture planning and debugging
- **Cursor AI**: Intelligent code editing and refactoring

### AI-Assisted Development
- **GitHub Copilot**: Code completion and suggestion (~30% of code)
- **Claude**: Architecture planning, debugging, and code review
- **AI-Generated**: Employee dataset, FastAPI endpoints, RAG pipeline structure

### Development Process
- **Code Generation**: ~40% AI-assisted, 60% hand-written
- **Architecture Design**: AI helped design RAG pipeline and FastAPI structure
- **Data Processing**: AI generated realistic employee dataset and embeddings logic
- **Error Handling**: AI suggested robust exception handling patterns
- **UI Development**: AI-assisted Streamlit interface with progress indicators
- **Model Integration**: AI helped switch from transformers to GGUF implementation

### Manual Implementation
- **Business Logic**: Custom query parsing and filtering algorithms
- **Performance Optimization**: GGUF model configuration and timeout handling
- **User Experience**: Custom Streamlit interface design and interaction flow
- **Debugging**: Manual troubleshooting of import issues and model loading

## 🛠 Technical Decisions

### Why GGUF over transformers?
- **Simplicity**: Single file model, easier deployment
- **Performance**: Optimized for CPU inference
- **Resource Efficiency**: Lower memory usage than full transformers
- **No Authentication**: No HuggingFace login required

### RAG Architecture Choices
- **Sentence Transformers**: Fast, efficient embeddings for semantic search
- **Cosine Similarity**: Simple but effective for employee matching
- **GGUF + llama-cpp-python**: Efficient local inference
- **JSON Storage**: Simple data layer for rapid prototyping

### Performance vs Cost vs Privacy Trade-offs
- **Performance**: Chose smaller models for faster response times
- **Cost**: Local deployment eliminates API costs
- **Privacy**: All employee data stays on-premises
- **Scalability**: Can upgrade to larger models or vector databases

### Technology Stack Rationale
- **FastAPI**: Automatic API docs, async support, type hints
- **Streamlit**: Rapid UI development with minimal code
- **PyTorch**: Flexible deep learning framework
- **Sentence Transformers**: Pre-trained models for embeddings

## 🧪 Testing the System

### Sample Queries to Try
```
1. "Find Python developers with 3+ years experience"
2. "Who has worked on healthcare projects?"
3. "I need someone for a React Native mobile app"
4. "Find ML engineers available for a new project"
5. "Show me backend developers who know AWS"
6. "Who can work on a microservices architecture?"
7. "Find someone with both frontend and backend skills"
8. "I need a DevOps engineer familiar with Kubernetes"
```

### Expected Response Format
```
Based on your requirements for Python developers with 3+ years experience, I found 3 excellent candidates:

**Alice Johnson** would be perfect for this role. She has 5 years of experience as a Full Stack Developer and her skills include Python, React, AWS, Docker, and PostgreSQL. She's currently available and has worked on projects like E-commerce Platform and Healthcare Dashboard.

**Alex Turner** is another strong candidate with 3 years of experience as a Data Engineer. He specializes in Python, FastAPI, Machine Learning, and Data Analysis. He's available and has built systems like Recommendation Engine and Analytics Dashboard.

Both candidates have the Python expertise and experience level you're looking for. Would you like me to provide more details about their specific projects or check their availability for meetings?
```

## 🔧 Troubleshooting

### Common Issues

#### API Connection Error
```bash
# Check if API is running
curl http://localhost:8000/health

# Restart API server
uvicorn api.main:app --reload
```

#### Mistral Model Loading Issues
- **OutOfMemory**: Reduce model size or use CPU-only mode
- **Model Not Found**: Check model path in `.env` file
- **CUDA Issues**: Set `USE_CUDA=false` in `.env`

#### Streamlit Connection Issues
- Ensure API server is running on port 8000
- Check firewall settings
- Verify API_BASE_URL in streamlit_app.py

### Performance Optimization
- Use GPU for faster Mistral inference
- Enable model quantization (`LOAD_IN_8BIT=true`)
- Cache embeddings for repeated queries
- Use smaller top_k values for faster responses

## 🚀 Future Improvements

### Short-term Enhancements
- [ ] Add employee photo support
- [ ] Implement query history persistence
- [ ] Add export functionality for search results
- [ ] Include availability calendar integration
- [ ] Add skill recommendations based on project requirements

### Advanced Features
- [ ] **Vector Database**: Migrate to Pinecone/Weaviate for better scalability
- [ ] **Fine-tuned Models**: Train custom embeddings on HR domain
- [ ] **Multi-modal Search**: Add resume/document search capabilities
- [ ] **Real-time Updates**: Live employee data synchronization
- [ ] **Analytics Dashboard**: Query patterns and usage statistics
- [ ] **Integration APIs**: Connect with HRIS systems (Workday, BambooHR)

### Enterprise Features
- [ ] **Role-based Access**: Different permissions for different users
- [ ] **Audit Logging**: Track all queries and data access
- [ ] **SSO Integration**: Active Directory/LDAP authentication
- [ ] **Compliance**: GDPR/CCPA data protection features
- [ ] **Multi-tenant**: Support multiple organizations

## 📊 Demo

### Live Demo Features
1. **Natural Language Chat**: Interactive conversation with AI
2. **Advanced Search**: Filter-based employee discovery
3. **Statistics Dashboard**: Workforce analytics and insights
4. **Real-time Results**: Instant semantic search responses


## 🔒 Security & Privacy

### Data Protection
- Employee data stored locally only
- No external API calls for sensitive information
- Configurable data retention policies
- Optional data encryption at rest

### Access Control
- API key authentication (configurable)
- Rate limiting on endpoints
- Input validation and sanitization
- CORS protection for frontend

## 📈 Performance Metrics

### Benchmarks
- **Query Response Time**: ~2-5 seconds (with GPU)
- **Embedding Generation**: ~500ms for 16 employees
- **Memory Usage**: ~4GB (Mistral) + 1GB (embeddings)
- **Concurrent Users**: Tested with 10+ simultaneous queries

### Scalability Considerations
- Horizontal scaling with multiple API instances
- Database migration for >1000 employees
- Caching layer for frequent queries
- Load balancing for high availability

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Mistral AI for the language model
- Sentence Transformers for embedding models
- FastAPI and Streamlit communities
- HuggingFace for model hosting and tools

## 📞 Support

For questions or support:
- Create an issue in the repository
- Check existing documentation
- Review troubleshooting section

---

**Built with ❤️ for modern HR teams**