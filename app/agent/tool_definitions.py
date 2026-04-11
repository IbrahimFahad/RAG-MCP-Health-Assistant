# Tool definitions in Claude API format.
# Claude reads these and decides which tool to call based on the user question.

TOOL_DEFINITIONS = [
    {
        "name": "web_search",
        "description": (
            "Search the web for health information using Tavily. "
            "Use this when the knowledge base does not have a good answer. "
            "Returns a list of relevant articles with titles, URLs, and content snippets."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The health question or topic to search for. Can be in Arabic or English."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return. Default is 5.",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "scrape_url",
        "description": (
            "Scrape and extract the full text content from a health webpage. "
            "Use this after web_search to get the complete article content from a trusted URL."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the webpage to scrape."
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "pubmed_search",
        "description": (
            "Search PubMed for peer-reviewed scientific articles from the NIH database. "
            "Use this for clinical questions, drug information, or when the user needs evidence-based medical information."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The medical topic or clinical question to search for."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of articles to return. Default is 3.",
                    "default": 3
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "store_to_db",
        "description": (
            "Store new health information into the vector knowledge base. "
            "Always call this after retrieving useful content from web_search or pubmed_search, "
            "so future questions on the same topic are answered from the database."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The health content to store."
                },
                "title": {
                    "type": "string",
                    "description": "Title or topic of the content."
                },
                "source_url": {
                    "type": "string",
                    "description": "The URL where this content was retrieved from."
                },
                "source_type": {
                    "type": "string",
                    "description": "Source type: 'web', 'pubmed', or 'manual'.",
                    "enum": ["web", "pubmed", "manual"]
                }
            },
            "required": ["text", "title"]
        }
    },
    {
        "name": "calculate_bmi",
        "description": (
            "Calculate Body Mass Index (BMI) given weight and height. "
            "Returns BMI value, WHO category (underweight/normal/overweight/obese), and health advice."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "weight_kg": {
                    "type": "number",
                    "description": "Body weight in kilograms."
                },
                "height_cm": {
                    "type": "number",
                    "description": "Height in centimeters."
                }
            },
            "required": ["weight_kg", "height_cm"]
        }
    },
    {
        "name": "calculate_bmr",
        "description": (
            "Calculate Basal Metabolic Rate (BMR) and daily calorie needs "
            "using the Mifflin-St Jeor equation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "weight_kg":      {"type": "number", "description": "Body weight in kilograms."},
                "height_cm":      {"type": "number", "description": "Height in centimeters."},
                "age_years":      {"type": "integer", "description": "Age in years."},
                "gender":         {"type": "string", "description": "'male' or 'female'.", "enum": ["male", "female"]},
                "activity_level": {
                    "type": "string",
                    "description": "Activity level: sedentary, light, moderate, active, or very_active.",
                    "enum": ["sedentary", "light", "moderate", "active", "very_active"],
                    "default": "moderate"
                }
            },
            "required": ["weight_kg", "height_cm", "age_years", "gender"]
        }
    },
    {
        "name": "calculate_ideal_weight",
        "description": "Calculate ideal body weight using the Devine formula.",
        "input_schema": {
            "type": "object",
            "properties": {
                "height_cm": {"type": "number", "description": "Height in centimeters."},
                "gender":    {"type": "string", "description": "'male' or 'female'.", "enum": ["male", "female"]}
            },
            "required": ["height_cm", "gender"]
        }
    },
]
