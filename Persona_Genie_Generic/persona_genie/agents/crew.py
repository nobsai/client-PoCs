from crewai import Agent, Task, Crew
from langchain.tools import tool
from langchain_openai import ChatOpenAI
import os
import sys

# Add project root to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_processor import get_customer_stats

class CustomerProfilerCrew:
    """
    CrewAI-based crew for customer profiling
    """
    
    def __init__(self, verbose=False, api_key=None):
        """Initialize the Customer Profiler Crew"""
        self.verbose = verbose
        self.api_key = api_key
        
        # Configure LLM to use the API key
        if api_key:
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                openai_api_key=api_key
            )
        
    def create_style_analyst(self):
        """Create the Style Analyst agent"""
        return Agent(
            role="Luxury Style Analyst",
            goal="Analyze customer purchase patterns to determine style preferences and aesthetic tastes",
            backstory="""You are an expert in luxury fashion and lifestyle trends. 
            With years of experience in high-end retail analytics, you can discern subtle patterns
            in purchasing behavior that reveal a customer's style philosophy and aesthetic preferences.
            You have a keen eye for how product choices reflect personality.""",
            verbose=self.verbose,
            allow_delegation=False,
            max_rpm=20,  # Optimize API usage
            openai_api_key=self.api_key,
            llm=self.llm if hasattr(self, 'llm') else None
        )
        
    def create_persona_writer(self):
        """Create the Persona Writer agent"""
        return Agent(
            role="Customer Persona Storyteller",
            goal="Craft elegant, narrative-driven customer personas that read like high-end fashion profiles",
            backstory="""You are a gifted writer specializing in luxury brand storytelling.
            Your prose is elegant and insightful, capturing the essence of identity through consumption choices.
            You create vivid character sketches that help luxury brands understand their clientele on a
            deeper, more emotional level.""",
            verbose=self.verbose,
            allow_delegation=False,
            max_rpm=20,  # Optimize API usage
            openai_api_key=self.api_key,
            llm=self.llm if hasattr(self, 'llm') else None
        )
        
    def create_archetype_classifier(self):
        """Create the Archetype Classifier agent"""
        return Agent(
            role="Fashion Archetype Specialist",
            goal="Classify customers into relevant fashion and lifestyle archetypes",
            backstory="""You are a specialist in categorizing consumer behavior into meaningful archetypes.
            You understand the difference between 'The Urban Nomad' and 'The Heritage Enthusiast.'
            Your classifications are nuanced, avoiding clichés while providing actionable insights for
            luxury retailers.""",
            verbose=self.verbose,
            allow_delegation=False,
            max_rpm=20,  # Optimize API usage
            openai_api_key=self.api_key,
            llm=self.llm if hasattr(self, 'llm') else None
        )
    
    def analyze_style_preferences(self, customer_orders):
        """
        Analyze a customer's style preferences based on their order history
        
        Args:
            customer_orders: List of order dictionaries for a customer
            
        Returns:
            String containing context for the analysis
        """
        # Get basic customer stats
        stats = get_customer_stats(customer_orders)
        
        # Extract relevant information for analysis
        products = [order['Product Name'] for order in customer_orders]
        categories = [order['Category'] for order in customer_orders]
        colors = [order['Color'] for order in customer_orders]
        brands = [order['Brand'] for order in customer_orders]
        
        # Construct context string for the agent
        context = f"""
        Customer Purchase History:
        - Products: {', '.join(products[:10])}{'...' if len(products) > 10 else ''}
        - Categories: {', '.join(set(categories))}
        - Colors: {', '.join(set(colors))}
        - Brands: {', '.join(set(brands))}
        - Total Spent: ${stats['total_spent']}
        - Order Count: {stats['order_count']}
        - Favorite Categories: {', '.join(stats['favorite_categories'])}
        - Favorite Colors: {', '.join(stats['favorite_colors'])}
        - Preferred Channels: {', '.join(stats['preferred_channels'])}
        """
        
        return context
    
    def get_customer_profile(self, customer_id, customer_orders):
        """
        Generate a comprehensive customer profile
        
        Args:
            customer_id: ID of the customer
            customer_orders: List of order dictionaries for the customer
            
        Returns:
            Dictionary containing the customer profile
        """
        # Get customer stats first to avoid redundant processing
        stats = get_customer_stats(customer_orders)
        
        # If the customer has very few orders, create a simplified profile
        if len(customer_orders) <= 2:
            return self._create_simplified_profile(customer_id, customer_orders, stats)
        
        # Create agents
        style_analyst = self.create_style_analyst()
        persona_writer = self.create_persona_writer()
        archetype_classifier = self.create_archetype_classifier()
        
        # Create context for agents
        purchase_analysis = self.analyze_style_preferences(customer_orders)
        
        # Create tasks with optimized prompts
        style_analysis_task = Task(
            description=f"""
            Analyze this customer's purchase history and identify their style preferences.
            
            Purchase History:
            {purchase_analysis}
            
            Your analysis should cover:
            1. Style preferences (minimalist, luxury, streetwear, etc.)
            2. Color affinity
            3. Price sensitivity
            4. Brand loyalty or diversity
            
            Keep your analysis concise but insightful.
            """,
            agent=style_analyst,
            expected_output="A concise analysis of the customer's style preferences."
        )
        
        lifestyle_analysis_task = Task(
            description=f"""
            Based on the purchase history, infer lifestyle traits and values of this customer.
            
            Purchase History:
            {purchase_analysis}
            
            Your analysis should identify:
            1. Inferred lifestyle traits (e.g., traveler, collector, sport-driven)
            2. Emotional values (comfort, uniqueness, prestige)
            
            Be brief but insightful.
            """,
            agent=style_analyst,
            expected_output="A brief analysis of lifestyle traits and values."
        )
        
        archetype_task = Task(
            description=f"""
            Create a stylish archetype for this customer based on their purchase history.
            
            Purchase History:
            {purchase_analysis}
            
            Simply provide an archetype name (e.g., "The Urban Nomad", "The Prestige Minimalist")
            and a one-sentence explanation.
            """,
            agent=archetype_classifier,
            expected_output="An archetype name and brief explanation."
        )
        
        persona_task = Task(
            description=f"""
            Create a short, elegant persona summary for this customer.
            
            Purchase History:
            {purchase_analysis}
            
            Write a stylish, concise profile (2-3 lines) that captures their essence.
            """,
            agent=persona_writer,
            expected_output="A short narrative customer profile."
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[style_analyst, persona_writer, archetype_classifier],
            tasks=[style_analysis_task, lifestyle_analysis_task, archetype_task, persona_task],
            verbose=self.verbose,
            process="sequential",  # Process tasks sequentially for reliability
            openai_api_key=self.api_key,
            llm=self.llm if hasattr(self, 'llm') else None
        )
        
        try:
            # Run the crew and get results as a CrewOutput object
            result = crew.kickoff()
            
            # Access the specific task outputs from the CrewOutput object
            style_analysis = result.outputs.get(style_analysis_task.id, "Style analysis not available.")
            lifestyle_analysis = result.outputs.get(lifestyle_analysis_task.id, "Lifestyle analysis not available.")
            archetype = result.outputs.get(archetype_task.id, "Archetype not available.")
            persona = result.outputs.get(persona_task.id, "Persona not available.")
            
            # Combine with stats to create the complete profile
            profile = {
                'customer_id': customer_id,
                'total_spent': stats['total_spent'],
                'order_count': stats['order_count'],
                'favorite_brands': stats['favorite_brands'],
                'favorite_categories': stats['favorite_categories'],
                'favorite_colors': stats['favorite_colors'],
                'style_analysis': style_analysis,
                'lifestyle_analysis': lifestyle_analysis,
                'archetype': archetype,
                'persona': persona,
                'product_keywords': stats.get('product_keywords', [])
            }
            
            return profile
            
        except Exception as e:
            # Fallback to simplified profile in case of errors
            print(f"Error in CrewAI processing: {e}")
            return self._create_simplified_profile(customer_id, customer_orders, stats)
    
    def _create_simplified_profile(self, customer_id, customer_orders, stats):
        """Create a simplified profile when full analysis can't be performed"""
        
        # Simple style analysis based on categories and colors
        style_preferences = []
        if "Footwear" in stats['favorite_categories']:
            style_preferences.append("footwear-focused")
        if "Apparel" in stats['favorite_categories']:
            style_preferences.append("apparel-conscious")
        if "Accessories" in stats['favorite_categories']:
            style_preferences.append("accessory-oriented")
        
        style_description = "versatile" if len(style_preferences) > 1 else "specialized"
        
        # Brand loyalty check
        brand_loyalty = "brand loyal" if len(stats['favorite_brands']) <= 2 else "brand explorer"
        
        # Color preferences
        color_theme = "vibrant" if any(c in ["Racing Red", "Sapphire Blue", "Emerald Green"] for c in stats['favorite_colors']) else "subdued"
        
        # Construct basic profile
        style_analysis = f"This customer shows a {style_description} style with a preference for {', '.join(stats['favorite_categories'])}. They appear to be {brand_loyalty} and favor a {color_theme} color palette."
        
        lifestyle_analysis = f"Based on their purchasing patterns, this customer values quality and has shown interest in {', '.join(stats['favorite_brands'])} products."
        
        archetype = f"The {color_theme.capitalize()} {style_description.capitalize()}"
        
        persona = f"A discerning client with an eye for {', '.join(stats['favorite_categories']).lower()} from select brands. Their choices reflect a {color_theme} aesthetic sensibility and {brand_loyalty} approach to luxury."
        
        return {
            'customer_id': customer_id,
            'total_spent': stats['total_spent'],
            'order_count': stats['order_count'],
            'favorite_brands': stats['favorite_brands'],
            'favorite_categories': stats['favorite_categories'],
            'favorite_colors': stats['favorite_colors'],
            'style_analysis': style_analysis,
            'lifestyle_analysis': lifestyle_analysis,
            'archetype': archetype,
            'persona': persona,
            'product_keywords': stats.get('product_keywords', [])
        } 
