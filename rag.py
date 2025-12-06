import os
import json
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain

# Load environment variables
load_dotenv()


class CareerGuideRAG:
    def __init__(self, pdf_path: str = None):
        # Initialize Groq client
        self.groq_api_key = os.getenv('groq_api_key')
        self.llm = ChatGroq(
            temperature=0.7,
            model_name="llama-3.3-70b-versatile",
            api_key=self.groq_api_key
        )

        # Initialize document store
        self.vector_store = None
        if pdf_path:
            self._initialize_vector_store(pdf_path)

        # Initialize prompt templates
        self._initialize_prompts()

    def _initialize_vector_store(self, pdf_path: str):
        """Initialize the vector store with PDF documents"""
        try:
            # Load PDF document
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()

            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            texts = text_splitter.split_documents(documents)

            # Create embeddings and vector store
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.vector_store = Chroma.from_documents(texts, embeddings)

        except Exception as e:
            print(f"Error initializing vector store: {str(e)}")
            raise

    def _initialize_prompts(self):
        """Initialize prompt templates"""
        self.role_recommendation_template = """
        You are an AI assistant inside a career guidance application.
IMPORTANT: You MUST provide personalized career recommendations based EXACTLY on the user's specific profile below.
DO NOT return generic recommendations - tailor each recommendation to match the user's unique skills, interests, and background.

The user has provided the following information:

Personal Information:
- Name: {name}
- Field of Study: {field_of_study}

Skills:
- Technical Skills: {technical_skills}
- Soft Skills: {soft_skills}

Interests & Preferences:
- Subjects Enjoyed: {subjects_enjoyed}
- Preferred Industries: {preferred_industries}

CRITICAL: Analyze the user's specific technical skills, soft skills, field of study, and preferred industries.
Recommend career roles that DIRECTLY align with these specific attributes.
For example:
- If the user has Python, Machine Learning skills → recommend Data Scientist, ML Engineer, AI Researcher
- If the user has Java, Spring Boot skills → recommend Backend Developer, Software Engineer, Java Developer
- If the user prefers Healthcare industry → recommend Healthcare IT roles, Medical Data Analyst, etc.

Based on THIS SPECIFIC USER'S PROFILE, recommend 5-10 career roles that would be a good fit.
For each role, generate a PURE JSON object with the following structure:

{{
  "role": "Role Name",
  "match_score": 85,
  "reason": "Brief explanation of why this role is a good fit",
  "skills": ["Skill1", "Skill2", "Skill3"],
  "roadmap": [
    "Step 1: Learn basics",
    "Step 2: Take courses",
    "Step 3: Build projects",
    "step 4: Apply for jobs",
    "step 5:               ",
    "step 6:               "
  ],
  "companies": [
    {{
      "name": "Company A",
      "logo": "https://example.com/logo1.png",
      "tag": "Tech Giant",
      "description": "Short description about the company",
      "salary_range": "₹80,000 - ₹120,000"
    }}
  ],
  "courses": [
    {{
      "name": "Course Title",
      "duration": "3 months",
      "link": "https://example.com/course1"
    }}
  ]
}}

Rules:
- Return a JSON array of 3-5 role objects
- Use emojis in roadmap steps for better readability
- Keep company and course details concise but informative
- Include realistic salary ranges for each company based on the role and company size (e.g., "$80,000 - $120,000" for entry-level, "$120,000 - $180,000" for mid-level, "$150,000 - $250,000" for senior roles)
- Ensure the response is valid JSON that can be parsed directly
- If you have access to the provided context, use it to enhance your recommendations
- If no context is available, use your general knowledge

Context from career documents:
{context}

Return ONLY the JSON array, no other text or markdown formatting.
"""

        self.role_details_template = """You are a career guidance assistant providing detailed information about the role: {role_name}

User's Background:
- Field of Study: {field_of_study}
- Technical Skills: {technical_skills}
- Soft Skills: {soft_skills}

Generate a comprehensive JSON object with the following structure:

{{
  "title": "{role_name}",
  "description": "Detailed description of the role",
  "skills": ["Skill 1", "Skill 2", "Skill 3"],
  "roadmap": [
    "Step 1: Learn basics",
    "Step 2: Take courses",
    "Step 3: Build projects",
    "Step 4: Apply for jobs",
    "step 5:               ",
    "step 6:               "
  ],
  "companies": [
    {{
      "name": "Company Name",
      "logo": "https://example.com/logo.png",
      "tag": "Company Type",
      "description": "Brief description",
      "salary_range": "₹80,000 - ₹120,000"
    }}
  ],
  "courses": [
    {{
      "name": "Course Title",
      "duration": "3 months",
      "url": "https://example.com/course"
    }}
  ]
}}

Context from career documents:
{context}

IMPORTANT: Include realistic salary ranges for each company based on the role, company size, and location. 
Format salary ranges as "₹X,XXX - ₹X,XXX" (e.g., "₹80,000 - ₹120,000" for entry-level, "₹120,000 - ₹180,000" for mid-level, "₹150,000 - ₹250,000" for senior roles at top companies).

Return ONLY the JSON object, no other text or markdown formatting.
"""

    def _get_relevant_context(self, query: str, k: int = 3) -> str:
        """Retrieve relevant context from the vector store"""
        if not self.vector_store:
            return "No additional context available."

        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return "\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            print(f"Error retrieving context: {str(e)}")
            return "Error retrieving context."

    def get_career_recommendations(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get career recommendations based on user profile"""
        try:
            # Prepare context
            context_query = f"""
            Career recommendations for someone with:
            - Field of study: {profile_data['personal']['field_of_study']}
            - Technical skills: {', '.join(profile_data['skills']['technical_skills'])}
            - Preferred industries: {', '.join(profile_data['interests']['preferred_industries'])}
            """
            context = self._get_relevant_context(context_query)

            # Format the prompt
            prompt = PromptTemplate(
                template=self.role_recommendation_template,
                input_variables=["name", "field_of_study", "technical_skills",
                                 "soft_skills", "subjects_enjoyed", "preferred_industries", "context"]
            )

            # Format the input
            technical_skills_str = ', '.join(profile_data['skills']['technical_skills']) if profile_data['skills']['technical_skills'] else 'None specified'
            soft_skills_str = ', '.join(profile_data['skills']['soft_skills']) if profile_data['skills']['soft_skills'] else 'None specified'
            subjects_str = ', '.join(profile_data['interests']['subjects_enjoyed']) if profile_data['interests']['subjects_enjoyed'] else 'None specified'
            industries_str = ', '.join(profile_data['interests']['preferred_industries']) if profile_data['interests']['preferred_industries'] else 'None specified'
            
            formatted_prompt = prompt.format(
                name=profile_data['personal'].get('name', 'User'),
                field_of_study=profile_data['personal'].get('field_of_study', 'Not specified'),
                technical_skills=technical_skills_str,
                soft_skills=soft_skills_str,
                subjects_enjoyed=subjects_str,
                preferred_industries=industries_str,
                context=context
            )
            
            # Debug: Print the formatted prompt to verify data is being passed


            # Get response from LLM
            response = self.llm.invoke(formatted_prompt)

            # Parse the response
            recommendations = json.loads(response.content)
            return recommendations

        except Exception as e:
            print(f"Error getting career recommendations: {str(e)}")
            return self._get_default_recommendations()

    def get_role_details(self, role_name: str, profile_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get detailed information about a specific role"""
        try:
            # Prepare context
            context = self._get_relevant_context(f"Detailed information about {role_name} career")

            # Format the prompt
            prompt = PromptTemplate(
                template=self.role_details_template,
                input_variables=["role_name", "field_of_study", "technical_skills", "soft_skills", "context"]
            )

            # Get user's skills if available
            field_of_study = profile_data['personal']['field_of_study'] if profile_data else "Not specified"
            tech_skills = ', '.join(profile_data['skills']['technical_skills']) if profile_data else "Not specified"
            soft_skills = ', '.join(profile_data['skills']['soft_skills']) if profile_data else "Not specified"

            # Format the input
            formatted_prompt = prompt.format(
                role_name=role_name,
                field_of_study=field_of_study,
                technical_skills=tech_skills,
                soft_skills=soft_skills,
                context=context
            )

            # Get response from LLM
            response = self.llm.invoke(formatted_prompt)

            # Parse the response
            role_details = json.loads(response.content)
            return role_details

        except Exception as e:
            print(f"Error getting role details: {str(e)}")
            return {
                'title': role_name,
                'description': f'Error loading details for {role_name}.',
                'skills': [],
                'roadmap': [],
                'companies': [],
                'courses': []
            }

    def _get_default_recommendations(self) -> List[Dict[str, Any]]:
        """Return default recommendations in case of API failure"""
        return [
            {
                'title': 'Data Scientist',
                'match_score': 85,
                'reason': 'Matches your technical skills and analytical interests',
                'skills': ['Python', 'Machine Learning', 'Data Analysis', 'Statistics'],
                'roadmap': [
                    '🚀 Learn Python and data analysis libraries',
                    '📊 Study statistics and machine learning',
                    '💻 Work on data science projects',
                    '🏢 Apply for data science internships'
                ],
                'companies': [
                    {
                        'name': 'Google',
                        'logo': 'https://logo.clearbit.com/google.com',
                        'tag': 'Tech Giant',
                        'description': 'Leading technology company specializing in Internet-related services and products.',
                        'salary_range': '$120,000 - $200,000'
                    }
                ],
                'courses': [
                    {
                        'name': 'Data Science Specialization',
                        'duration': '6 months',
                        'url': 'https://www.coursera.org/specializations/jhu-data-science'
                    }
                ]
            }
        ]


# Example usage
if __name__ == "__main__":
    # Initialize with a PDF file
    rag = CareerGuideRAG(pdf_path="career_resources.pdf")

    # Example profile data
    profile = {
        'personal': {
            'name': 'vishnu',
            'field_of_study': 'cse,3rd year'
        },
        'skills': {
            'technical_skills': ['JAVA', 'C++', 'Spring Boot'],
            'soft_skills': ['Communication', 'Problem Solving']
        },
        'interests': {
            'subjects_enjoyed': ['Mathematics', 'DSA', 'Programming'],
            'preferred_industries': ['Technology', 'Finance', 'Healthcare']
        }
    }

    # Get recommendations
    recommendations = rag.get_career_recommendations(profile)
    print("Recommended Roles:", json.dumps(recommendations, indent=2))

    # Get role details
    if recommendations:
        role_name = recommendations[0]['role']
        role_details = rag.get_role_details(role_name, profile)
        print(f"\\nDetails for {role_name}:", json.dumps(role_details, indent=2))