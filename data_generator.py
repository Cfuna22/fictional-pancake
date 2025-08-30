import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import logging

class CRMDataGenerator:
    def __init__(self):
        self.fake = Faker()
        Faker.seed(42)  # For reproducible results
        np.random.seed(42)
        random.seed(42)
        
        # Define realistic company domains and industry keywords
        self.company_domains = [
            'gmail.com', 'outlook.com', 'company.com', 'business.org', 
            'enterprise.net', 'corp.com', 'inc.com', 'solutions.com'
        ]
        
        # Sentiment keywords for generating realistic feedback
        self.positive_keywords = [
            'excellent', 'amazing', 'fantastic', 'love', 'perfect', 'outstanding',
            'impressed', 'satisfied', 'helpful', 'efficient', 'professional'
        ]
        
        self.negative_keywords = [
            'terrible', 'awful', 'disappointed', 'frustrated', 'slow', 'unhelpful',
            'confusing', 'expensive', 'difficult', 'broken', 'poor'
        ]
        
        self.neutral_keywords = [
            'okay', 'average', 'standard', 'acceptable', 'decent', 'normal',
            'expected', 'typical', 'regular', 'adequate'
        ]
        
        # Pain points for negative feedback
        self.pain_points = [
            'slow response times', 'complicated interface', 'expensive pricing',
            'poor customer support', 'technical issues', 'billing problems',
            'lack of features', 'integration difficulties', 'training needed',
            'system downtime', 'data migration issues', 'security concerns'
        ]

    def generate_customers(self, num_customers=500, regions=None, segments=None):
        """Generate realistic customer data"""
        if regions is None:
            regions = ['North America', 'Europe', 'APAC']
        if segments is None:
            segments = ['SMB', 'Mid-Market', 'Enterprise']
        
        customers = []
        
        for i in range(num_customers):
            customer_id = f"CUST_{i+1:05d}"
            
            # Generate realistic customer profile
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            company_name = self.fake.company()
            
            customer = {
                'Customer_ID': customer_id,
                'Customer_Name': f"{first_name} {last_name}",
                'Company_Name': company_name,
                'Email': f"{first_name.lower()}.{last_name.lower()}@{random.choice(self.company_domains)}",
                'Phone': self.fake.phone_number(),
                'Segment': np.random.choice(segments, p=[0.5, 0.3, 0.2]),  # Weighted towards SMB
                'Region': np.random.choice(regions, p=[0.4, 0.35, 0.25]),  # Weighted towards North America
                'Industry': self.fake.random_element([
                    'Technology', 'Healthcare', 'Finance', 'Manufacturing', 
                    'Retail', 'Education', 'Government', 'Non-Profit'
                ]),
                'Company_Size': self._get_company_size(),
                'Account_Manager': f"{self.fake.first_name()} {self.fake.last_name()}",
                'Created_Date': self.fake.date_between(start_date='-2y', end_date='today'),
                'Last_Activity': self.fake.date_between(start_date='-30d', end_date='today'),
                'Annual_Revenue': self._get_annual_revenue(),
                'Status': np.random.choice(['Active', 'Inactive', 'Churned'], p=[0.8, 0.15, 0.05])
            }
            customers.append(customer)
        
        return pd.DataFrame(customers)

    def generate_deals(self, customers_df):
        """Generate realistic deal data for customers"""
        deals = []
        deal_stages = ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']
        
        # Generate 1-3 deals per customer on average
        for _, customer in customers_df.iterrows():
            num_deals = np.random.poisson(1.5) + 1  # At least 1 deal
            
            for i in range(min(num_deals, 5)):  # Cap at 5 deals per customer
                deal_id = f"DEAL_{customer['Customer_ID']}_{i+1}"
                
                # Deal size based on segment
                deal_size = self._get_deal_size(customer['Segment'])
                
                # Stage probability based on customer status
                stage_probs = self._get_stage_probabilities(customer['Status'])
                stage = np.random.choice(deal_stages, p=stage_probs)
                
                deal = {
                    'Deal_ID': deal_id,
                    'Customer_ID': customer['Customer_ID'],
                    'Deal_Name': f"{customer['Company_Name']} - {self.fake.random_element(['License', 'Subscription', 'Implementation', 'Upgrade', 'Renewal'])}",
                    'Deal_Size': deal_size,
                    'Stage': stage,
                    'Close_Probability': self._get_close_probability(stage),
                    'Expected_Close_Date': self._get_expected_close_date(stage),
                    'Created_Date': self.fake.date_between(start_date='-1y', end_date='today'),
                    'Owner': customer['Account_Manager'],
                    'Product': self.fake.random_element([
                        'CRM Platform', 'Analytics Suite', 'Integration Package', 
                        'Premium Support', 'Custom Development', 'Training Services'
                    ]),
                    'Source': self.fake.random_element([
                        'Inbound Lead', 'Referral', 'Cold Outreach', 'Marketing Campaign', 
                        'Existing Customer', 'Partner'
                    ])
                }
                deals.append(deal)
        
        return pd.DataFrame(deals)

    def generate_feedback(self, customers_df):
        """Generate realistic customer feedback and sentiment data"""
        feedback = []
        
        # Generate 1-5 feedback entries per customer
        for _, customer in customers_df.iterrows():
            num_feedback = np.random.poisson(2) + 1  # At least 1 feedback
            
            for i in range(min(num_feedback, 8)):  # Cap at 8 feedback per customer
                feedback_id = f"FB_{customer['Customer_ID']}_{i+1}"
                
                # Generate sentiment based on customer status and segment
                sentiment_score, sentiment_label = self._generate_sentiment(customer)
                churn_risk = self._calculate_churn_risk(sentiment_score, customer)
                
                feedback_text = self._generate_feedback_text(sentiment_score, customer)
                
                feedback_entry = {
                    'Feedback_ID': feedback_id,
                    'Customer_ID': customer['Customer_ID'],
                    'Feedback_Text': feedback_text,
                    'Sentiment_Score': sentiment_score,
                    'Sentiment_Label': sentiment_label,
                    'Churn_Risk': churn_risk,
                    'Feedback_Date': self.fake.date_between(start_date='-6m', end_date='today'),
                    'Feedback_Channel': self.fake.random_element([
                        'Email', 'Phone', 'Survey', 'Chat', 'Social Media', 'Support Ticket'
                    ]),
                    'Category': self.fake.random_element([
                        'Product Quality', 'Customer Service', 'Pricing', 'Features', 
                        'Performance', 'Support', 'Implementation', 'Training'
                    ]),
                    'Region': customer['Region'],
                    'Segment': customer['Segment'],
                    'Resolved': np.random.choice([True, False], p=[0.8, 0.2]),
                    'Response_Time_Hours': np.random.exponential(24) if sentiment_score < 0 else np.random.exponential(12)
                }
                feedback.append(feedback_entry)
        
        return pd.DataFrame(feedback)

    def _get_company_size(self):
        """Generate realistic company size based on segment distribution"""
        size_options = ['1-10', '11-50', '51-200', '201-1000', '1000+']
        return np.random.choice(size_options, p=[0.3, 0.25, 0.2, 0.15, 0.1])

    def _get_annual_revenue(self):
        """Generate realistic annual revenue"""
        return np.random.lognormal(mean=12, sigma=1.5) * 1000  # Log-normal distribution

    def _get_deal_size(self, segment):
        """Generate deal size based on customer segment"""
        if segment == 'Enterprise':
            return np.random.normal(150000, 50000)
        elif segment == 'Mid-Market':
            return np.random.normal(50000, 15000)
        else:  # SMB
            return np.random.normal(15000, 5000)

    def _get_stage_probabilities(self, status):
        """Get stage probabilities based on customer status"""
        if status == 'Churned':
            return [0.1, 0.1, 0.1, 0.1, 0.1, 0.5]  # Mostly closed lost
        elif status == 'Inactive':
            return [0.3, 0.2, 0.2, 0.1, 0.1, 0.1]  # Early stages
        else:  # Active
            return [0.2, 0.25, 0.2, 0.15, 0.15, 0.05]  # Normal distribution

    def _get_close_probability(self, stage):
        """Get close probability based on deal stage"""
        probabilities = {
            'Prospecting': np.random.uniform(0.1, 0.3),
            'Qualification': np.random.uniform(0.2, 0.4),
            'Proposal': np.random.uniform(0.4, 0.6),
            'Negotiation': np.random.uniform(0.6, 0.8),
            'Closed Won': 1.0,
            'Closed Lost': 0.0
        }
        return probabilities.get(stage, 0.5)

    def _get_expected_close_date(self, stage):
        """Get expected close date based on stage"""
        if stage in ['Closed Won', 'Closed Lost']:
            return self.fake.date_between(start_date='-90d', end_date='today')
        else:
            days_ahead = {
                'Prospecting': 90,
                'Qualification': 60,
                'Proposal': 30,
                'Negotiation': 15
            }
            return self.fake.date_between(start_date='today', 
                                        end_date=f'+{days_ahead.get(stage, 45)}d')

    def _generate_sentiment(self, customer):
        """Generate sentiment score and label based on customer characteristics"""
        base_sentiment = 0
        
        # Adjust based on customer status
        if customer['Status'] == 'Churned':
            base_sentiment -= 0.5
        elif customer['Status'] == 'Inactive':
            base_sentiment -= 0.2
        
        # Adjust based on segment (Enterprise customers might be more demanding)
        if customer['Segment'] == 'Enterprise':
            base_sentiment -= 0.1
        elif customer['Segment'] == 'SMB':
            base_sentiment += 0.1
        
        # Add random variation
        sentiment_score = np.clip(base_sentiment + np.random.normal(0, 0.3), -1, 1)
        
        # Convert to label
        if sentiment_score > 0.2:
            sentiment_label = 'Positive'
        elif sentiment_score < -0.2:
            sentiment_label = 'Negative'
        else:
            sentiment_label = 'Neutral'
        
        return round(sentiment_score, 3), sentiment_label

    def _calculate_churn_risk(self, sentiment_score, customer):
        """Calculate churn risk based on sentiment and customer factors"""
        risk_score = 0
        
        # Sentiment impact (most important factor)
        if sentiment_score < -0.5:
            risk_score += 0.6
        elif sentiment_score < 0:
            risk_score += 0.3
        elif sentiment_score > 0.5:
            risk_score -= 0.2
        
        # Customer status impact
        if customer['Status'] == 'Churned':
            return 'High'  # Already churned
        elif customer['Status'] == 'Inactive':
            risk_score += 0.3
        
        # Segment impact
        if customer['Segment'] == 'Enterprise':
            risk_score -= 0.1  # Less likely to churn due to switching costs
        
        # Random factor
        risk_score += np.random.uniform(-0.1, 0.1)
        
        # Convert to category
        if risk_score > 0.6:
            return 'High'
        elif risk_score > 0.3:
            return 'Medium'
        else:
            return 'Low'

    def _generate_feedback_text(self, sentiment_score, customer):
        """Generate realistic feedback text based on sentiment"""
        templates = {
            'positive': [
                "The {product} has been {positive_word}! Our team is very {positive_word} with the results.",
                "Excellent {category}. The support team was {positive_word} and {positive_word}.",
                "We're {positive_word} with the {product}. It has {positive_word} our workflow significantly.",
                "Outstanding experience! The {category} exceeded our expectations.",
                "The platform is {positive_word} and our productivity has {positive_word} dramatically."
            ],
            'negative': [
                "Very {negative_word} experience. We're having issues with {pain_point}.",
                "The {product} is {negative_word} and we're experiencing {pain_point}.",
                "Frustrated with {pain_point}. The service has been {negative_word}.",
                "The {category} needs improvement. We're dealing with {pain_point}.",
                "Disappointed with the {negative_word} {category} and ongoing {pain_point}."
            ],
            'neutral': [
                "The {product} is {neutral_word}. It meets our basic requirements.",
                "Average experience with {category}. Nothing exceptional but {neutral_word}.",
                "The service is {neutral_word}. Some areas could be improved.",
                "Standard {product} with {neutral_word} performance.",
                "The platform is {neutral_word} for our needs."
            ]
        }
        
        if sentiment_score > 0.2:
            template = random.choice(templates['positive'])
            feedback = template.format(
                product=random.choice(['platform', 'software', 'solution', 'system']),
                positive_word=random.choice(self.positive_keywords),
                category=random.choice(['service', 'support', 'implementation', 'training'])
            )
        elif sentiment_score < -0.2:
            template = random.choice(templates['negative'])
            feedback = template.format(
                product=random.choice(['platform', 'software', 'solution', 'system']),
                negative_word=random.choice(self.negative_keywords),
                pain_point=random.choice(self.pain_points),
                category=random.choice(['service', 'support', 'implementation', 'pricing'])
            )
        else:
            template = random.choice(templates['neutral'])
            feedback = template.format(
                product=random.choice(['platform', 'software', 'solution', 'system']),
                neutral_word=random.choice(self.neutral_keywords),
                category=random.choice(['service', 'support', 'performance', 'features'])
            )
        
        return feedback

    def generate_complete_dataset(self, num_customers=500, regions=None, segments=None):
        """Generate complete CRM dataset with all tables"""
        logging.info(f"Generating complete dataset for {num_customers} customers")
        
        # Generate customers
        customers_df = self.generate_customers(num_customers, regions, segments)
        logging.info(f"Generated {len(customers_df)} customers")
        
        # Generate deals
        deals_df = self.generate_deals(customers_df)
        logging.info(f"Generated {len(deals_df)} deals")
        
        # Generate feedback
        feedback_df = self.generate_feedback(customers_df)
        logging.info(f"Generated {len(feedback_df)} feedback entries")
        
        # Calculate summary statistics
        summary_stats = self._calculate_summary_stats(customers_df, deals_df, feedback_df)
        
        return customers_df, deals_df, feedback_df, summary_stats

    def _calculate_summary_stats(self, customers_df, deals_df, feedback_df):
        """Calculate summary statistics for the generated data"""
        stats = {
            'total_customers': len(customers_df),
            'total_deals': len(deals_df),
            'total_feedback': len(feedback_df),
            'avg_sentiment': round(feedback_df['Sentiment_Score'].mean(), 3),
            'churn_risk_high': len(feedback_df[feedback_df['Churn_Risk'] == 'High']),
            'churn_risk_percent': round((len(feedback_df[feedback_df['Churn_Risk'] == 'High']) / len(feedback_df)) * 100, 1),
            'total_pipeline': round(deals_df[deals_df['Stage'].isin(['Prospecting', 'Qualification', 'Proposal', 'Negotiation'])]['Deal_Size'].sum(), 0),
            'won_deals': len(deals_df[deals_df['Stage'] == 'Closed Won']),
            'lost_deals': len(deals_df[deals_df['Stage'] == 'Closed Lost']),
            'regions': customers_df['Region'].value_counts().to_dict(),
            'segments': customers_df['Segment'].value_counts().to_dict(),
            'sentiment_by_region': feedback_df.groupby('Region')['Sentiment_Score'].mean().round(3).to_dict(),
            'sentiment_by_segment': feedback_df.groupby('Segment')['Sentiment_Score'].mean().round(3).to_dict()
        }
        
        return stats
