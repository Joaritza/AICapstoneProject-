# Plant Based Assistant - Complete Implementation Plan

**Project Title:** Plant Based Assistant Chatbot  
**Goal:** Build a production-ready Python chatbot that achieves "Excellent (4)" across all rubric categories  
**Timeline:** Phased implementation with clear milestones  

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Rubric Alignment Strategy](#rubric-alignment-strategy)
3. [System Architecture](#system-architecture)
4. [Data Source Integration](#data-source-integration)
5. [AI Orchestration Design](#ai-orchestration-design)
6. [Implementation Roadmap](#implementation-roadmap)
7. [File Structure & Responsibilities](#file-structure--responsibilities)
8. [Dependencies & Environment Setup](#dependencies--environment-setup)
9. [Error Handling Strategy](#error-handling-strategy)
10. [Documentation Plan](#documentation-plan)

---

## Project Overview

### Core Functionality
The Plant Based Assistant combines four key capabilities:
1. **Ingredient Analysis** - Determine if ingredients are vegan with reasoning
2. **Vegan Alternatives** - Suggest substitutions for non-vegan ingredients
3. **Recipe Recommendations** - Find recipes based on ingredients or dietary needs
4. **Nutrition Insights** - Provide protein, calorie, and nutritional information

### Key Differentiator
Multi-step reasoning across integrated data sources (not simple Q&A). The AI orchestration layer synthesizes information from multiple APIs/databases to provide comprehensive, context-aware responses.

---

## Rubric Alignment Strategy

### 1. Data Source Integration (25 points) → EXCELLENT TIER
**Target:** 13-15 pts (Robust, diverse sources with excellent error handling)

**Three Data Sources:**
1. **USDA FoodData Central API** (Free)
   - Purpose: Ingredient database + nutrition info
   - Endpoint: `https://fdc.nal.usda.gov/api/food/search`
   - Data: Complete nutrition, ingredient lists

2. **Spoonacular API** (Free tier available)
   - Purpose: Recipe database + meal planning
   - Endpoints: Search recipes, get recipe details, find by ingredients
   - Data: 5+ million recipes, dietary tags, nutrition

3. **Custom Vegan Ingredients Database** (CSV-based, self-maintained)
   - Purpose: Vegan/non-vegan ingredient classification
   - Data: Ingredient name → vegan status, common alternatives
   - Fallback: Used when APIs rate-limited or offline

**Function Design:**
```python
# Core functions to implement
- get_ingredient_info(ingredient_name) → nutrition, vegan_status
- get_vegan_alternatives(ingredient) → [alternatives] with explanations
- find_recipes(ingredients, dietary_prefs) → [recipes with full details]
- analyze_product(product_name) → full ingredient breakdown + analysis
```

**Error Handling:**
- API rate limit handling with exponential backoff
- Fallback to CSV database when APIs unavailable
- Graceful degradation with cached responses
- Clear user messaging on data freshness

---

### 2. AI Orchestration (25 points) → EXCELLENT TIER
**Target:** 13-15 pts for library usage + 9-10 pts for conversation management

**Orchestration Library:** LangChain (primary choice)
- Why: Mature ecosystem, excellent tool calling, conversation memory
- Alternative: LlamaIndex (for document-heavy scenarios)

**Agent Architecture:**
```
User Input
    ↓
[Conversation Memory Manager]
    ↓
[Router Agent] - Determines which tools needed
    ├→ [Ingredient Analysis Subagent]
    │   ├→ Tool: get_ingredient_vegan_status()
    │   ├→ Tool: get_nutrition_info()
    │   └→ Tool: find_alternatives()
    ├→ [Recipe Finder Subagent]
    │   ├→ Tool: search_recipes_by_ingredients()
    │   ├→ Tool: filter_by_dietary_prefs()
    │   └→ Tool: get_recipe_nutrition()
    └→ [Meal Planner Subagent]
        ├→ Tool: analyze_user_preferences()
        ├→ Tool: fetch_recipes_for_week()
        └→ Tool: generate_shopping_list()
    ↓
[Response Synthesizer] - Combine outputs from multiple sources
    ↓
[Conversation Memory Updater]
    ↓
User Response
```

**Conversation Management:**
- Memory: Store user preferences, ingredients on hand, dietary goals
- Context Window: Full conversation history with relevance scoring
- State Management: User profile evolves with each interaction
- Follow-up Handling: Queries build on previous responses

---

### 3. Response Quality & Data Utilization (20 points) → EXCELLENT TIER
**Target:** 11-12 pts for accuracy + 7-8 pts for synthesis

**Response Design Pattern:**
```
User: "Is milk vegan? What's a good alternative?"

System Process:
1. [Ingredient Analysis Tool] → Milk is NOT vegan (dairy origin)
2. [Explanation Tool] → Reason: Animal-derived product
3. [Alternatives Tool] → Top 5 substitutes (nutritional match)
4. [Nutrition Comparison Tool] → Compare protein/calcium
5. [Recipe Integration] → 3 recipes using best alternative

Response: [Structured, multi-layered answer with reasoning]
```

**Information Synthesis Examples:**
- Multiple source attribution ("According to USDA data... and recipe databases show...")
- Conflicting information handling (if sources differ on vegan status)
- Nutritional trade-offs explanation
- Practical recipe integration

---

### 4. Technical Implementation (15 points) → EXCELLENT TIER
**Target:** 7-8 pts architecture + 6-7 pts error handling

**Architecture Principles:**
- **Separation of Concerns:**
  - `data_sources/` - API clients, caching, fallbacks
  - `agents/` - LangChain agent definitions
  - `tools/` - Tool implementations (functions called by agents)
  - `ui/` - User interface layer
  - `utils/` - Logging, config, constants
  
- **Clean Code:**
  - Type hints throughout
  - Comprehensive docstrings
  - DRY principle followed
  - Single responsibility per module

**Error Handling:**
- Custom exception hierarchy
- API failure detection with fallback logic
- Network timeout handling
- User-friendly error messages
- Logging for debugging and monitoring

---

### 5. User Experience & Interface (10 points) → EXCELLENT TIER
**Target:** 5 pts interface + 5 pts guidance

**UI Features:**
- Nature-themed design (green palette, plant imagery)
- Clear suggested prompts on startup
- Typing indicators and response streaming
- Error messages with recovery suggestions
- Conversation history sidebar
- User preferences panel

**Guidance Elements:**
- Onboarding flow explaining capabilities
- "Examples you can ask" section
- Help commands with detailed explanations
- Clear display of data sources used
- Confidence levels for recommendations

---

### 6. Documentation & Presentation (5 points) → EXCELLENT TIER
**Target:** 3 pts documentation + 2 pts presentation

**Deliverables:**
- README.md with setup instructions
- Architecture diagrams (system, data flow, agent decision tree)
- API documentation (each tool with examples)
- Video demonstration (5-10 minutes)
- Code comments and docstrings

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                 │
│         (Streamlit/Gradio - Nature Themed)             │
└────────────┬────────────────────────────────┬───────────┘
             │                                │
    ┌────────▼──────────┐        ┌──────────▼──────┐
    │ Chat Interface    │        │ Settings Panel  │
    │ - Message input   │        │ - Preferences   │
    │ - Chat history    │        │ - API keys      │
    │ - Suggestions     │        │ - Model config  │
    └────────┬──────────┘        └──────────┬──────┘
             │                                │
             └────────────────┬───────────────┘
                              │
         ┌────────────────────▼─────────────────────┐
         │   ORCHESTRATION LAYER (LangChain)       │
         │  ┌─────────────────────────────────┐   │
         │  │ Conversation Memory Manager     │   │
         │  │ - Context window (last 10 msgs) │   │
         │  │ - User preferences storage      │   │
         │  │ - Session state                 │   │
         │  └─────────────────────────────────┘   │
         │  ┌─────────────────────────────────┐   │
         │  │ Router Agent (Claude/GPT-4)     │   │
         │  │ - Determines required tools     │   │
         │  │ - Creates execution plan        │   │
         │  │ - Delegates to subagents        │   │
         │  └─────────────────────────────────┘   │
         │  ┌──────────┬──────────┬───────────┐   │
         │  │Ingredient│ Recipe   │  Meal     │   │
         │  │  Agent   │Finder    │ Planner   │   │
         │  │          │ Agent    │  Agent    │   │
         │  └──────┬───┴──┬───────┴──────┬────┘   │
         │  ┌──────▼──────▼──────────────▼──┐    │
         │  │  Response Synthesizer          │    │
         │  │  - Combine outputs             │    │
         │  │  - Verify consistency          │    │
         │  │  - Format for readability      │    │
         │  └────────────────────────────────┘    │
         └──────────────┬──────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
  ┌─────▼────────┐ ┌───▼──────────┐ ┌──▼─────────────┐
  │ TOOL LAYER   │ │ CACHE LAYER  │ │ERROR HANDLING  │
  │              │ │              │ │                │
  │- Functions   │ │- Redis cache │ │- Retry logic   │
  │  called by   │ │- File cache  │ │- Fallbacks     │
  │  agents      │ │- TTL mgmt    │ │- Exceptions    │
  └─────┬────────┘ └──────┬───────┘ └────┬───────────┘
        │                 │               │
        └─────────────────┼───────────────┘
                          │
          ┌───────────────┴───────────────┐
          │   DATA SOURCE LAYER           │
          │                               │
    ┌─────▼──────────┐ ┌────────────────┐ │
    │ USDA API Client│ │Spoonacular API │ │
    │ - Search foods │ │ - Search recipes│ │
    │ - Get nutrition│ │ - Get details  │ │
    │ - Error handle │ │ - Error handle │ │
    └────────────────┘ └────────────────┘ │
                                           │
    ┌──────────────────────────────────┐ │
    │ Vegan Database (CSV + SQLite)    │ │
    │ - Ingredient classification      │ │
    │ - Alternative suggestions        │ │
    │ - Local fallback                 │ │
    └──────────────────────────────────┘ │
                                          │
└──────────────────────────────────────────┘
```

---

## Data Source Integration

### Data Source 1: USDA FoodData Central API

**Purpose:** Comprehensive ingredient/food database with complete nutritional information

**Endpoints:**
```
Base URL: https://fdc.nal.usda.gov/api/food

GET /search?query={ingredient}&pageSize=10
Returns: Food items with FDC IDs, descriptions

GET /food/{fdc_id}
Returns: Full nutritional data, ingredients, serving sizes
```

**Data Structure:**
```python
{
  "food": {
    "fdcId": "544638",
    "description": "Milk, lowfat, fluid, 2% milkfat, with added vitamin A and D",
    "foodNutrients": [
      {
        "nutrient": {"name": "Energy"},
        "value": 49  # kcal per 100g
      },
      {
        "nutrient": {"name": "Protein"},
        "value": 3.2  # grams
      }
    ]
  }
}
```

**Implementation:**
- Wrapper class: `USDAFoodClient`
- Rate limiting: 120 requests/minute (free tier)
- Caching: 24-hour TTL on nutrition data

---

### Data Source 2: Spoonacular Recipe API

**Purpose:** Recipe database with dietary tags, ingredients, and instructions

**Endpoints:**
```
GET /recipes/findByIngredients
  ?ingredients={comma-separated}&number=10&ranking=1

GET /recipes/{id}/information
  ?includeNutrition=true

GET /recipes/{id}/nutrition
```

**Data Structure:**
```python
{
  "id": 594736,
  "title": "Pasta with Garlic, Scallions, and Breadcrumbs",
  "image": "url",
  "diets": ["vegan", "vegetarian"],  # KEY FIELD
  "extendedIngredients": [
    {
      "id": 20027,
      "name": "pasta",
      "amount": 1,
      "unit": "pound"
    }
  ],
  "nutrition": {
    "calories": 567,
    "protein": 21,
    "carbs": 98,
    "fat": 5
  }
}
```

**Implementation:**
- Wrapper class: `SpoonacularRecipeClient`
- Rate limiting: 150 requests/day (free tier) or upgrade
- Caching: 7-day TTL on recipes (stable data)

---

### Data Source 3: Custom Vegan Database (CSV/SQLite)

**Purpose:** Local ingredient classification and alternative suggestions

**Structure (vegan_ingredients.csv):**
```csv
ingredient,vegan,reason,alternatives,alternatives_explained
Milk,FALSE,"Animal product - from cow lactation","Oat Milk|Almond Milk|Soy Milk","Plant-based with similar protein (soy)|Lower protein but popular (oat)|Creamy texture (almond)"
Chicken Egg,FALSE,"Animal product - from chickens","Flax Egg|Chickpea Flour|Applesauce","Binding & leavening|Protein-rich baking|Moisture in baking"
Honey,FALSE,"Bee product - unclear ethics for vegans","Maple Syrup|Agave|Brown Rice Syrup","Similar sweetness (maple)|Lower glycemic (agave)|Neutral flavor (rice)"
Tofu,TRUE,"Soy-based, plant origin",,"Already vegan"
```

**Implementation:**
- Store as SQLite database (faster queries)
- Keep CSV as backup
- Local fallback when APIs unavailable
- Update monthly from curated sources

---

## AI Orchestration Design

### LangChain Architecture

**Core Components:**

#### 1. Tools (Functions Called by Agents)
```python
# tools/ingredient_tools.py
@tool
def check_ingredient_vegan_status(ingredient: str) -> dict:
    """Check if an ingredient is vegan with detailed explanation."""
    # Queries all three data sources
    # Returns: {"name": "", "vegan": bool, "reason": "", "sources": []}

@tool
def get_vegan_alternatives(ingredient: str, limit: int = 5) -> list:
    """Get vegan alternatives with nutritional comparison."""
    # Returns: [{"alternative": "", "reason": "", "nutrition_match": ""}]

@tool
def search_recipes(ingredients: list[str], dietary_prefs: dict) -> list:
    """Find recipes matching ingredients and preferences."""
    # Returns: [{"name": "", "url": "", "nutrition": {}, "difficulty": ""}]

@tool
def get_ingredient_nutrition(ingredient: str, amount: float, unit: str) -> dict:
    """Get precise nutrition info for ingredient + amount."""
    # Returns: {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0}

@tool
def analyze_meal(recipe_url: str) -> dict:
    """Full nutritional analysis of a complete recipe."""
    # Returns: comprehensive nutrition breakdown + vegan status
```

#### 2. Agents

**Router Agent (Main Decision Maker)**
```python
router_agent = AgentExecutor.from_agent_and_tools(
    agent=ChatOpenAI(model="gpt-4", temperature=0).with_system_prompt(
        """You are the main router agent. Analyze the user query and determine:
        1. What type of request is this? (ingredient check, recipe search, meal planning, nutrition)
        2. Which tools are needed?
        3. What order should tools be called?
        4. What follow-up clarifications might be needed?
        
        Then execute the appropriate subagent or tools to fulfill the request."""
    ),
    tools=[
        check_ingredient_vegan_status,
        get_vegan_alternatives,
        search_recipes,
        get_ingredient_nutrition,
        analyze_meal
    ],
    memory=ConversationBufferWindowMemory(k=10),  # Remember last 10 exchanges
    verbose=True
)
```

**Ingredient Analysis Subagent**
- Specialized in ingredient queries
- Combines vegan status + alternatives + recipes using that ingredient
- Calls multiple tools in sequence

**Recipe Finder Subagent**
- Specialized in recipe searches
- Filters by dietary preferences
- Provides detailed nutritional analysis

**Conversation Memory**
```python
memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    k=10,  # Keep last 10 exchanges
    human_prefix="User",
    ai_prefix="Assistant"
)

# Plus extended user profile:
user_profile = {
    "dietary_restrictions": [],
    "ingredients_on_hand": [],
    "protein_goal": 50,
    "budget": "moderate",
    "cuisine_preferences": [],
    "allergies": []
}
```

#### 3. Response Synthesis
```python
synthesizer = ResponseSynthesizer(
    format_rules={
        "include_sources": True,
        "explain_reasoning": True,
        "provide_alternatives": True,
        "suggest_recipes": True,
        "cite_nutrition": True
    }
)
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
**Goal:** Set up project structure, environment, and basic data source connections

**Deliverables:**
- [ ] Project directory structure created
- [ ] Python virtual environment configured (.venv)
- [ ] requirements.txt with all dependencies
- [ ] .env file template with API keys
- [ ] Basic logging infrastructure
- [ ] Unit test framework set up

**Key Files to Create:**
- `main.py` - Entry point
- `config.py` - Configuration management
- `requirements.txt` - Dependencies
- `.env.example` - Environment variable template
- `setup.py` - Package configuration
- `tests/` directory with test structure

---

### Phase 2: Data Source Integration (Week 2-3)
**Goal:** Implement robust API clients with error handling and caching

**Deliverables:**
- [ ] USDA API client with rate limiting
- [ ] Spoonacular API client with rate limiting
- [ ] Vegan ingredients CSV/database
- [ ] Caching layer (Redis or file-based)
- [ ] Error handling for all data sources
- [ ] Fallback mechanisms tested

**Key Files:**
- `data_sources/usda_client.py`
- `data_sources/spoonacular_client.py`
- `data_sources/vegan_database.py`
- `data_sources/cache_manager.py`
- `utils/exceptions.py` - Custom exceptions
- `utils/retry_logic.py` - Retry strategies

**Testing:**
- Mock API responses
- Test fallback scenarios
- Verify caching behavior
- Load testing on concurrent requests

---

### Phase 3: Tool Functions (Week 3-4)
**Goal:** Implement all tool functions that agents will call

**Deliverables:**
- [ ] All 5+ core tool functions implemented
- [ ] Type hints and comprehensive docstrings
- [ ] Unit tests for each tool (80%+ coverage)
- [ ] Tools tested with real data

**Key Files:**
- `tools/ingredient_tools.py`
- `tools/recipe_tools.py`
- `tools/nutrition_tools.py`
- `tests/test_tools.py`

**Tools to Implement:**
1. `check_ingredient_vegan_status()`
2. `get_vegan_alternatives()`
3. `search_recipes_by_ingredients()`
4. `get_ingredient_nutrition()`
5. `analyze_recipe_nutrition()`
6. `generate_shopping_list()`
7. `get_recipe_instructions()`

---

### Phase 4: LangChain Agent Implementation (Week 4-5)
**Goal:** Build the orchestration layer with agents and conversation management

**Deliverables:**
- [ ] Router agent implemented and tested
- [ ] Subagents for ingredient/recipe/nutrition queries
- [ ] Conversation memory management
- [ ] Multi-turn conversation handling
- [ ] Agent decision-making verified

**Key Files:**
- `agents/router_agent.py`
- `agents/ingredient_agent.py`
- `agents/recipe_agent.py`
- `agents/meal_planner_agent.py`
- `agents/response_synthesizer.py`
- `agents/memory_manager.py`
- `tests/test_agents.py`

**Testing:**
- Integration tests with mock LLM responses
- Conversation flow tests
- Agent decision-making verification
- Multi-step reasoning validation

---

### Phase 5: User Interface (Week 5-6)
**Goal:** Build intuitive, nature-themed interface

**Deliverables:**
- [ ] Streamlit/Gradio UI built
- [ ] Chat interface with message history
- [ ] Settings panel for user preferences
- [ ] Suggested prompts displayed
- [ ] Error message handling
- [ ] Response formatting with sources

**Key Files:**
- `ui/app.py` - Main interface
- `ui/components.py` - Reusable UI components
- `ui/styling.py` - CSS/theming
- `ui/prompts.py` - Suggested questions

**Design Elements:**
- Green/nature color palette
- Plant-themed icons
- Clear typography
- Responsive layout
- Mobile-friendly

---

### Phase 6: Error Handling & Robustness (Week 6)
**Goal:** Comprehensive error handling and graceful degradation

**Deliverables:**
- [ ] Custom exception hierarchy
- [ ] Error handling for all code paths
- [ ] API failure handling with fallbacks
- [ ] Network timeout management
- [ ] User-friendly error messages
- [ ] Logging infrastructure

**Error Scenarios to Handle:**
- API rate limits exceeded → Use cached data + fallback DB
- API timeout → Retry with exponential backoff
- Unknown ingredient → Clear explanation + suggestions
- Invalid user input → Guided correction
- Network unavailable → Offline mode with local data
- Missing .env keys → Clear setup instructions

---

### Phase 7: Testing & Quality Assurance (Week 6-7)
**Goal:** Comprehensive testing and code quality verification

**Deliverables:**
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests for all workflows
- [ ] End-to-end testing scenarios
- [ ] Performance benchmarking
- [ ] Security review (API key handling)
- [ ] Code review & cleanup

**Testing Coverage:**
- `test_data_sources.py` - API clients
- `test_tools.py` - Tool functions
- `test_agents.py` - Agent behavior
- `test_ui.py` - Interface interactions
- `test_error_handling.py` - Error scenarios
- `test_integration.py` - Full workflows

---

### Phase 8: Documentation & Demo (Week 7-8)
**Goal:** Complete documentation and create demonstration video

**Deliverables:**
- [ ] README.md with setup instructions
- [ ] Architecture documentation with diagrams
- [ ] API documentation for tools
- [ ] Code comments and docstrings complete
- [ ] Demo video (5-10 minutes)
- [ ] Deployment instructions
- [ ] GitHub repository initialized

**Documentation Files:**
- `README.md` - Main project documentation
- `ARCHITECTURE.md` - System design
- `API_DOCUMENTATION.md` - Tool reference
- `SETUP_INSTRUCTIONS.md` - Installation guide
- `DEPLOYMENT.md` - Production setup
- `.github/` - Issue templates, contribution guidelines

---

## File Structure & Responsibilities

```
plant-based-assistant/
├── main.py                          # Entry point
├── requirements.txt                 # Python dependencies
├── setup.py                         # Package configuration
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules
├── README.md                        # Main documentation
├── ARCHITECTURE.md                  # System design details
├── API_DOCUMENTATION.md             # Tool reference docs
├── SETUP_INSTRUCTIONS.md            # Installation guide
│
├── config/
│   ├── __init__.py
│   ├── settings.py                  # Configuration management
│   ├── constants.py                 # Project constants
│   └── logger_config.py             # Logging setup
│
├── data_sources/
│   ├── __init__.py
│   ├── usda_client.py               # USDA API client
│   ├── spoonacular_client.py        # Spoonacular API client
│   ├── vegan_database.py            # Local vegan DB interface
│   ├── cache_manager.py             # Caching layer
│   └── data/
│       └── vegan_ingredients.csv    # Ingredient classification
│
├── tools/
│   ├── __init__.py
│   ├── ingredient_tools.py          # Ingredient checking tools
│   ├── recipe_tools.py              # Recipe finding tools
│   ├── nutrition_tools.py           # Nutrition analysis tools
│   └── meal_planning_tools.py       # Meal planning tools
│
├── agents/
│   ├── __init__.py
│   ├── router_agent.py              # Main routing agent
│   ├── ingredient_agent.py          # Ingredient subagent
│   ├── recipe_agent.py              # Recipe subagent
│   ├── meal_planner_agent.py        # Meal planning subagent
│   ├── response_synthesizer.py      # Output formatting
│   └── memory_manager.py            # Conversation memory
│
├── ui/
│   ├── __init__.py
│   ├── app.py                       # Main Streamlit app
│   ├── components.py                # Reusable UI components
│   ├── styling.py                   # CSS and theming
│   ├── prompts.py                   # Suggested questions
│   └── assets/
│       ├── plant_icon.png
│       ├── logo.svg
│       └── style.css
│
├── utils/
│   ├── __init__.py
│   ├── exceptions.py                # Custom exception classes
│   ├── retry_logic.py               # Retry mechanisms
│   ├── validators.py                # Input validation
│   ├── formatting.py                # Response formatting
│   └── logging_util.py              # Logging utilities
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Pytest configuration
│   ├── test_data_sources.py         # API client tests
│   ├── test_tools.py                # Tool function tests
│   ├── test_agents.py               # Agent behavior tests
│   ├── test_ui.py                   # Interface tests
│   ├── test_error_handling.py       # Error scenario tests
│   ├── test_integration.py          # End-to-end tests
│   └── fixtures/
│       ├── mock_api_responses.py
│       └── sample_data.json
│
└── docs/
    ├── architecture_diagram.md      # Visual architecture
    ├── deployment_guide.md          # Production setup
    ├── api_examples.md              # Usage examples
    └── troubleshooting.md           # Common issues
```

---

## File Responsibilities

### Entry Point: `main.py`
- Initialize the application
- Load environment variables and configuration
- Start the UI (Streamlit/Gradio)
- Set up logging
- Handle graceful shutdown

### Configuration: `config/`
- **settings.py:** Load and manage all config (API keys, model choice, feature flags)
- **constants.py:** Hardcoded values (cache TTLs, rate limits, data schemas)
- **logger_config.py:** Centralized logging setup with file and console handlers

### Data Integration: `data_sources/`
- **usda_client.py:** USDA API wrapper with error handling, rate limiting, caching
- **spoonacular_client.py:** Spoonacular API wrapper with similar robustness
- **vegan_database.py:** SQLite interface for local ingredient data
- **cache_manager.py:** Redis/file-based caching with TTL management

### Tools: `tools/`
- **ingredient_tools.py:** Functions for vegan status checking, alternatives
- **recipe_tools.py:** Recipe search, filtering, detailed information retrieval
- **nutrition_tools.py:** Nutritional analysis and calculations
- **meal_planning_tools.py:** Meal planning and shopping list generation

### AI Orchestration: `agents/`
- **router_agent.py:** Main decision-making agent that routes requests
- **ingredient_agent.py:** Specialized agent for ingredient queries
- **recipe_agent.py:** Specialized agent for recipe searches
- **meal_planner_agent.py:** Specialized agent for meal planning
- **response_synthesizer.py:** Combines outputs from multiple sources
- **memory_manager.py:** Conversation history and user profile management

### User Interface: `ui/`
- **app.py:** Main Streamlit application logic
- **components.py:** Reusable UI elements (message, button components)
- **styling.py:** CSS/Streamlit theming for nature theme
- **prompts.py:** Suggested questions to guide users

### Utilities: `utils/`
- **exceptions.py:** Custom exception hierarchy
- **retry_logic.py:** Exponential backoff and retry mechanisms
- **validators.py:** Input validation and sanitization
- **formatting.py:** Response formatting and markdown rendering
- **logging_util.py:** Structured logging with context

### Testing: `tests/`
- Comprehensive unit and integration tests
- Mocked API responses for consistent testing
- Fixtures for sample data and test configurations

---

## Dependencies & Environment Setup

### Python Version
- **Requirement:** Python 3.9+
- **Recommended:** Python 3.11+ (LangChain best support)

### Core Dependencies

```
# requirements.txt

# AI & Orchestration
langchain==0.1.16
langchain-openai==0.0.11
openai==1.14.0

# Data Fetching
requests==2.31.0
httpx==0.25.0

# Data Processing
pandas==2.1.3
numpy==1.24.3

# Database & Caching
sqlalchemy==2.0.23
python-dotenv==1.0.0

# UI
streamlit==1.32.0
streamlit-chat==0.1.1

# Utilities
pydantic==2.5.0
python-dateutil==2.8.2

# Development & Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.23.0
black==23.12.1
flake8==6.1.0
mypy==1.7.1
```

### Environment Variables (.env)

```env
# API Keys
OPENAI_API_KEY=sk_...
SPOONACULAR_API_KEY=...
USDA_API_KEY=...  # Free from USDA

# LLM Configuration
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
CACHE_TYPE=file  # or 'redis'
CACHE_TTL_HOURS=24

# UI Settings
STREAMLIT_SERVER_PORT=8501
NATURE_THEME=True
```

### Setup Instructions

```bash
# 1. Clone repository
git clone https://github.com/yourusername/plant-based-assistant.git
cd plant-based-assistant

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Initialize database
python -c "from data_sources.vegan_database import init_db; init_db()"

# 6. Run tests
pytest tests/ --cov=.

# 7. Start application
streamlit run ui/app.py
```

---

## Error Handling Strategy

### Custom Exception Hierarchy

```python
# utils/exceptions.py

class PlanBasedAssistantError(Exception):
    """Base exception for all application errors"""
    pass

class APIError(PlanBasedAssistantError):
    """Base for API-related errors"""
    pass

class APIRateLimitError(APIError):
    """API rate limit exceeded"""
    def __init__(self, retry_after: int):
        self.retry_after = retry_after

class APITimeoutError(APIError):
    """API request timed out"""
    pass

class DataSourceError(PlanBasedAssistantError):
    """Data source unavailable"""
    pass

class IngredientNotFoundError(PlanBasedAssistantError):
    """Ingredient not found in any database"""
    pass

class ConfigurationError(PlanBasedAssistantError):
    """Configuration or environment variable missing"""
    pass

class ValidationError(PlanBasedAssistantError):
    """Input validation failed"""
    pass
```

### Error Handling Patterns

#### Pattern 1: API Failure with Fallback
```python
def get_ingredient_nutrition(ingredient: str):
    """Try USDA API, fall back to Spoonacular, then local DB"""
    try:
        # Try primary source
        return usda_client.search_food(ingredient)
    except APIRateLimitError as e:
        logger.warning(f"USDA rate limited. Retrying in {e.retry_after}s")
        time.sleep(e.retry_after)
        return usda_client.search_food(ingredient)
    except APITimeoutError:
        logger.warning(f"USDA timeout, trying Spoonacular")
        return spoonacular_client.get_ingredient_info(ingredient)
    except APIError:
        logger.warning(f"APIs unavailable, using local database")
        return vegan_database.get_ingredient(ingredient)
```

#### Pattern 2: Input Validation
```python
def search_recipes(ingredients: list[str]) -> list:
    """Validate input before processing"""
    if not ingredients:
        raise ValidationError("At least one ingredient required")
    
    # Validate each ingredient
    for ing in ingredients:
        if not isinstance(ing, str) or len(ing.strip()) == 0:
            raise ValidationError(f"Invalid ingredient: {ing}")
    
    # Proceed with search
    return recipe_client.find_recipes(ingredients)
```

#### Pattern 3: Graceful User Messaging
```python
# In the agent's response formatting
def format_error_response(error: Exception) -> str:
    """Convert technical errors to user-friendly messages"""
    if isinstance(error, IngredientNotFoundError):
        return f"I couldn't find information about that ingredient. Try: ..."
    elif isinstance(error, APIRateLimitError):
        return "I'm getting a lot of requests right now. Please wait a moment and try again."
    elif isinstance(error, DataSourceError):
        return "I'm having trouble reaching my data sources. I can help with general vegan information."
    else:
        return "Something went wrong. Please try rephrasing your question."
```

### Error Scenarios & Handling

| Scenario | Detection | Response | Recovery |
|----------|-----------|----------|----------|
| API Rate Limit | HTTP 429 | Exponential backoff, use cache | Retry after delay |
| API Timeout | No response > 5s | Switch to fallback source | Retry with different API |
| Unknown Ingredient | Empty response | Clear message, suggest alternatives | Offer common alternatives |
| Missing .env Key | ConfigurationError on startup | Display setup instructions | Show which key is missing |
| Network Unavailable | ConnectionError | Use offline mode with cached data | Suggest reconnect |
| Malformed User Input | ValidationError | Ask for clarification | Show example format |

---

## Documentation Plan

### README.md (Main Documentation)
```markdown
# Plant Based Assistant

## Overview
[Project description, key features]

## Quick Start
[Installation and basic usage]

## Features
[Detailed feature descriptions]

## Architecture
[Link to ARCHITECTURE.md]

## API Reference
[Link to API_DOCUMENTATION.md]

## Development
[Setup for developers]

## Contributing
[Guidelines for contributions]

## License
[License information]
```

### ARCHITECTURE.md
```markdown
# System Architecture

## Overview
[System diagram and high-level components]

## Data Flow
[Diagrams showing data movement]

## AI Orchestration
[Agent architecture and decision trees]

## Data Sources
[Description of each integrated source]

## Error Handling
[Error scenarios and responses]

## Deployment
[Production setup]
```

### API_DOCUMENTATION.md
```markdown
# Tool & Function Reference

## check_ingredient_vegan_status()
Input: ingredient name
Output: vegan status with reasoning
Example: ...

## get_vegan_alternatives()
[Similar format for each tool]

## search_recipes()
...

## get_ingredient_nutrition()
...

## analyze_recipe_nutrition()
...
```

### Code Comments & Docstrings
Every function includes:
```python
def function_name(param1: str, param2: int) -> dict:
    """
    Short one-line description.
    
    Longer description explaining purpose, edge cases, and examples.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Dictionary with keys:
        - 'key1': Description
        - 'key2': Description
    
    Raises:
        ValueError: When inputs are invalid
        APIError: When API request fails
    
    Example:
        >>> result = function_name("test", 42)
        >>> result['key1']
        'value'
    """
```

---

## GitHub Integration & Deployment

### GitHub Setup

**Repository Structure:**
```
.github/
├── workflows/
│   ├── tests.yml              # Run tests on push
│   ├── linting.yml            # Code quality checks
│   └── deploy.yml             # Deploy on release
├── ISSUE_TEMPLATE/
│   └── bug_report.md
└── pull_request_template.md
```

**CI/CD Pipeline:**
1. **Tests Workflow** - Run pytest on every push
2. **Linting Workflow** - Black, Flake8, MyPy checks
3. **Deploy Workflow** - Deploy to production on release

### Environment Variable Management

**Development:**
```bash
cp .env.example .env
# Edit .env locally
# Never commit .env
```

**Production (GitHub Secrets):**
```
Settings → Secrets and Variables → Actions
Add:
- OPENAI_API_KEY
- SPOONACULAR_API_KEY
- USDA_API_KEY
- Other sensitive config
```

**In CI/CD:**
```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  SPOONACULAR_API_KEY: ${{ secrets.SPOONACULAR_API_KEY }}
```

### Deployment Options

#### Option 1: Streamlit Cloud (Easiest)
```bash
# Push to GitHub
# Connect repo to Streamlit Cloud
# Set secrets in Streamlit Cloud dashboard
# Auto-deploys on push
```

#### Option 2: Docker + Cloud Run/Heroku
```dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "ui/app.py"]
```

#### Option 3: VPS/Self-hosted
```bash
# Set up systemd service
# Use nginx as reverse proxy
# Enable SSL with Let's Encrypt
```

---

## Success Criteria (Rubric Mapping)

### Excellence Checklist

- ✅ **Data Source Integration (25 pts - Excellent Tier)**
  - [ ] 3+ diverse data sources integrated
  - [ ] Robust error handling for all APIs
  - [ ] Caching layer implemented
  - [ ] Fallback mechanisms tested
  - [ ] Rate limiting handled
  - [ ] All functions documented

- ✅ **AI Orchestration (25 pts - Excellent Tier)**
  - [ ] LangChain properly implemented
  - [ ] Router agent makes intelligent decisions
  - [ ] Conversation memory maintains context
  - [ ] Multi-turn queries work correctly
  - [ ] Subagents coordinate effectively
  - [ ] Response synthesis combines multiple sources

- ✅ **Response Quality (20 pts - Excellent Tier)**
  - [ ] Responses consistently accurate
  - [ ] Multiple sources cited
  - [ ] Reasoning explained clearly
  - [ ] Conflicting info handled appropriately
  - [ ] Recipes integrated meaningfully
  - [ ] Nutrition details provided when relevant

- ✅ **Technical Implementation (15 pts - Excellent Tier)**
  - [ ] Clean code architecture
  - [ ] Proper separation of concerns
  - [ ] Type hints throughout
  - [ ] Comprehensive error handling
  - [ ] 80%+ test coverage
  - [ ] Follows Python best practices

- ✅ **User Experience (10 pts - Excellent Tier)**
  - [ ] Intuitive interface design
  - [ ] Nature-themed visuals
  - [ ] Clear error messages
  - [ ] Helpful suggested prompts
  - [ ] Onboarding flow
  - [ ] Accessibility considerations

- ✅ **Documentation (5 pts - Excellent Tier)**
  - [ ] Complete README with setup
  - [ ] Architecture documentation
  - [ ] API reference
  - [ ] Code comments & docstrings
  - [ ] Demo video (5-10 min)
  - [ ] Deployment instructions

---

## Timeline & Milestones

| Week | Phase | Milestone | Deliverable |
|------|-------|-----------|------------|
| 1 | Foundation | Project setup complete | Directory structure, env setup |
| 2-3 | Data Integration | All APIs connected | API clients, caching, error handling |
| 3-4 | Tools | Tool functions ready | 5+ tested tools |
| 4-5 | Orchestration | Agents implemented | Router + subagents working |
| 5-6 | UI | Interface complete | Streamlit app, styling, prompts |
| 6 | Robustness | Error handling complete | All scenarios tested |
| 6-7 | Testing | Full test coverage | 80%+ coverage, all tests passing |
| 7-8 | Documentation | Complete | README, architecture docs, demo video |

---

## Next Steps

1. **Review this plan** with team/stakeholders
2. **Adjust scope** if needed (e.g., reduce to 2 data sources)
3. **Begin Phase 1** - Set up project structure and environment
4. **Track progress** using GitHub Issues/Projects
5. **Regular checkpoints** - Verify each phase completion

---

## Key Insights & Best Practices

### 1. Start with Data Quality
- Good data sources → Good agent decisions
- Test APIs thoroughly before building agents
- Cache aggressively to reduce API calls

### 2. Agent Design Matters
- Clear tool purposes help agents use them correctly
- Good prompts lead to better tool selection
- Memory management prevents confusion

### 3. Error Handling is Critical
- Users will enter unexpected queries
- APIs will fail sometimes
- Graceful degradation > Crashes

### 4. Testing Prevents Disasters
- Mock API responses for consistent testing
- Test error scenarios, not just happy paths
- Integration tests catch agent coordination issues

### 5. Documentation is a Feature
- Users need to understand what the bot can do
- Developers need to understand how to extend it
- Clear error messages = better user experience

---

**This plan achieves the "Excellent (4)" tier across all rubric categories.**
**Follow this roadmap sequentially for best results.**

