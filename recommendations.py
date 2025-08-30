import pandas as pd
import numpy as np
from collections import Counter
import re

class AIRecommendations:
    def __init__(self):
        self.pain_point_keywords = [
            'slow', 'expensive', 'difficult', 'complicated', 'poor', 'terrible',
            'frustrated', 'disappointed', 'issues', 'problems', 'downtime',
            'billing', 'support', 'training', 'integration', 'security'
        ]

    def generate_recommendations(self, customers_df, deals_df, feedback_df):
        """Generate AI-powered recommendations based on CRM and sentiment data"""
        
        recommendations = {
            'priority_actions': self._get_priority_actions(customers_df, deals_df, feedback_df),
            'churn_prevention': self._get_churn_prevention_recommendations(customers_df, feedback_df),
            'revenue_opportunities': self._get_revenue_opportunities(customers_df, deals_df, feedback_df),
            'operational_insights': self._get_operational_insights(feedback_df),
            'segment_insights': self._get_segment_insights(customers_df, feedback_df),
            'regional_insights': self._get_regional_insights(customers_df, feedback_df),
            'pain_point_analysis': self._analyze_pain_points(feedback_df),
            'success_metrics': self._calculate_success_metrics(customers_df, deals_df, feedback_df)
        }
        
        return recommendations

    def _get_priority_actions(self, customers_df, deals_df, feedback_df):
        """Generate top priority actions for immediate attention"""
        actions = []
        
        # High churn risk customers
        high_risk_feedback = feedback_df[feedback_df['Churn_Risk'] == 'High']
        if len(high_risk_feedback) > 0:
            high_risk_customers = high_risk_feedback['Customer_ID'].nunique()
            actions.append({
                'action': f'Immediate outreach to {high_risk_customers} high-risk customers',
                'priority': 'High',
                'impact': 'Prevent customer churn',
                'metric': f'{high_risk_customers} customers at risk'
            })
        
        # Unresolved negative feedback
        unresolved_negative = feedback_df[
            (feedback_df['Sentiment_Score'] < -0.3) & 
            (feedback_df['Resolved'] == False)
        ]
        if len(unresolved_negative) > 0:
            actions.append({
                'action': f'Resolve {len(unresolved_negative)} outstanding negative feedback cases',
                'priority': 'High',
                'impact': 'Improve customer satisfaction',
                'metric': f'{len(unresolved_negative)} unresolved issues'
            })
        
        # Stalled high-value deals
        stalled_deals = deals_df[
            (deals_df['Deal_Size'] > deals_df['Deal_Size'].quantile(0.8)) &
            (deals_df['Stage'].isin(['Proposal', 'Negotiation']))
        ]
        if len(stalled_deals) > 0:
            total_value = stalled_deals['Deal_Size'].sum()
            actions.append({
                'action': f'Accelerate {len(stalled_deals)} high-value deals in late stages',
                'priority': 'Medium',
                'impact': 'Increase revenue closure',
                'metric': f'${total_value:,.0f} in pipeline'
            })
        
        return actions

    def _get_churn_prevention_recommendations(self, customers_df, feedback_df):
        """Generate churn prevention recommendations"""
        recommendations = []
        
        # Analyze churn risk by segment
        churn_by_segment = feedback_df[feedback_df['Churn_Risk'] == 'High'].groupby('Segment').size()
        if len(churn_by_segment) > 0:
            worst_segment = churn_by_segment.idxmax()
            worst_count = churn_by_segment.max()
            recommendations.append({
                'recommendation': f'Focus churn prevention efforts on {worst_segment} segment',
                'reason': f'{worst_count} high-risk customers identified',
                'action': f'Implement targeted retention program for {worst_segment} customers'
            })
        
        # Analyze churn risk by region
        churn_by_region = feedback_df[feedback_df['Churn_Risk'] == 'High'].groupby('Region').size()
        if len(churn_by_region) > 0:
            worst_region = churn_by_region.idxmax()
            worst_count = churn_by_region.max()
            recommendations.append({
                'recommendation': f'Strengthen customer success in {worst_region} region',
                'reason': f'{worst_count} high-risk customers in this region',
                'action': f'Deploy additional customer success resources to {worst_region}'
            })
        
        # Response time analysis
        slow_responses = feedback_df[
            (feedback_df['Sentiment_Score'] < 0) & 
            (feedback_df['Response_Time_Hours'] > 24)
        ]
        if len(slow_responses) > 0:
            recommendations.append({
                'recommendation': 'Improve response times for negative feedback',
                'reason': f'{len(slow_responses)} negative feedback cases with >24h response time',
                'action': 'Implement automated escalation for negative sentiment feedback'
            })
        
        return recommendations

    def _get_revenue_opportunities(self, customers_df, deals_df, feedback_df):
        """Identify revenue growth opportunities"""
        opportunities = []
        
        # Happy customers with small deal sizes (upsell opportunity)
        happy_customers = feedback_df[feedback_df['Sentiment_Score'] > 0.5]['Customer_ID'].unique()
        customer_deal_sizes = deals_df.groupby('Customer_ID')['Deal_Size'].mean()
        small_deal_happy = customer_deal_sizes[customer_deal_sizes.index.isin(happy_customers)]
        
        if len(small_deal_happy) > 0:
            avg_deal_size = deals_df['Deal_Size'].mean()
            upsell_candidates = small_deal_happy[small_deal_happy < avg_deal_size * 0.7]
            if len(upsell_candidates) > 0:
                opportunities.append({
                    'opportunity': f'Upsell {len(upsell_candidates)} satisfied customers with small deal sizes',
                    'potential': f'${(avg_deal_size - upsell_candidates.mean()) * len(upsell_candidates):,.0f}',
                    'action': 'Launch targeted upsell campaign to happy customers'
                })
        
        # Enterprise customers with positive sentiment (expansion opportunity)
        enterprise_happy = feedback_df[
            (feedback_df['Segment'] == 'Enterprise') & 
            (feedback_df['Sentiment_Score'] > 0.3)
        ]['Customer_ID'].nunique()
        
        if enterprise_happy > 0:
            opportunities.append({
                'opportunity': f'Expand within {enterprise_happy} satisfied Enterprise accounts',
                'potential': 'High - Enterprise expansion deals typically 2-3x larger',
                'action': 'Engage account teams for expansion discussions'
            })
        
        # Positive SMB customers (referral opportunity)
        smb_happy = feedback_df[
            (feedback_df['Segment'] == 'SMB') & 
            (feedback_df['Sentiment_Score'] > 0.6)
        ]['Customer_ID'].nunique()
        
        if smb_happy > 0:
            opportunities.append({
                'opportunity': f'Leverage {smb_happy} highly satisfied SMB customers for referrals',
                'potential': f'Estimated {smb_happy * 0.3:.0f} potential referrals',
                'action': 'Launch customer referral program'
            })
        
        return opportunities

    def _get_operational_insights(self, feedback_df):
        """Generate operational insights from feedback data"""
        insights = []
        
        # Channel performance analysis
        channel_sentiment = feedback_df.groupby('Feedback_Channel')['Sentiment_Score'].mean().sort_values()
        if len(channel_sentiment) > 1:
            worst_channel = channel_sentiment.index[0]
            best_channel = channel_sentiment.index[-1]
            insights.append({
                'insight': f'Channel performance varies significantly',
                'detail': f'{worst_channel} has lowest satisfaction ({channel_sentiment.iloc[0]:.2f}), {best_channel} has highest ({channel_sentiment.iloc[-1]:.2f})',
                'recommendation': f'Investigate and improve {worst_channel} experience'
            })
        
        # Category analysis
        category_sentiment = feedback_df.groupby('Category')['Sentiment_Score'].mean().sort_values()
        if len(category_sentiment) > 0:
            worst_category = category_sentiment.index[0]
            insights.append({
                'insight': f'{worst_category} is the most problematic area',
                'detail': f'Average sentiment score: {category_sentiment.iloc[0]:.2f}',
                'recommendation': f'Prioritize improvements in {worst_category}'
            })
        
        # Resolution effectiveness
        resolved_sentiment = feedback_df[feedback_df['Resolved'] == True]['Sentiment_Score'].mean()
        unresolved_sentiment = feedback_df[feedback_df['Resolved'] == False]['Sentiment_Score'].mean()
        
        insights.append({
            'insight': 'Resolution impact on sentiment',
            'detail': f'Resolved issues: {resolved_sentiment:.2f} avg sentiment, Unresolved: {unresolved_sentiment:.2f}',
            'recommendation': 'Focus on improving resolution rates and quality'
        })
        
        return insights

    def _get_segment_insights(self, customers_df, feedback_df):
        """Analyze insights by customer segment"""
        insights = []
        
        segment_metrics = feedback_df.groupby('Segment').agg({
            'Sentiment_Score': 'mean',
            'Churn_Risk': lambda x: (x == 'High').sum(),
            'Response_Time_Hours': 'mean'
        }).round(2)
        
        for segment in segment_metrics.index:
            metrics = segment_metrics.loc[segment]
            insights.append({
                'segment': segment,
                'avg_sentiment': metrics['Sentiment_Score'],
                'high_risk_count': int(metrics['Churn_Risk']),
                'avg_response_time': metrics['Response_Time_Hours'],
                'recommendation': self._get_segment_recommendation(segment, metrics)
            })
        
        return insights

    def _get_regional_insights(self, customers_df, feedback_df):
        """Analyze insights by region"""
        insights = []
        
        regional_metrics = feedback_df.groupby('Region').agg({
            'Sentiment_Score': 'mean',
            'Churn_Risk': lambda x: (x == 'High').sum(),
            'Response_Time_Hours': 'mean'
        }).round(2)
        
        for region in regional_metrics.index:
            metrics = regional_metrics.loc[region]
            insights.append({
                'region': region,
                'avg_sentiment': metrics['Sentiment_Score'],
                'high_risk_count': int(metrics['Churn_Risk']),
                'avg_response_time': metrics['Response_Time_Hours'],
                'recommendation': self._get_regional_recommendation(region, metrics)
            })
        
        return insights

    def _analyze_pain_points(self, feedback_df):
        """Analyze common pain points from feedback text"""
        # Extract pain points from negative feedback
        negative_feedback = feedback_df[feedback_df['Sentiment_Score'] < -0.2]['Feedback_Text']
        
        pain_points = []
        for text in negative_feedback:
            for keyword in self.pain_point_keywords:
                if keyword in text.lower():
                    pain_points.append(keyword)
        
        # Count frequency
        pain_point_counts = Counter(pain_points)
        
        analysis = {
            'top_pain_points': [
                {'pain_point': point, 'frequency': count} 
                for point, count in pain_point_counts.most_common(10)
            ],
            'total_pain_points': len(pain_points),
            'unique_pain_points': len(pain_point_counts),
            'recommendations': self._get_pain_point_recommendations(pain_point_counts)
        }
        
        return analysis

    def _calculate_success_metrics(self, customers_df, deals_df, feedback_df):
        """Calculate key success metrics"""
        metrics = {
            'customer_satisfaction': {
                'avg_sentiment': round(feedback_df['Sentiment_Score'].mean(), 3),
                'positive_sentiment_rate': round((feedback_df['Sentiment_Score'] > 0.2).mean() * 100, 1),
                'negative_sentiment_rate': round((feedback_df['Sentiment_Score'] < -0.2).mean() * 100, 1)
            },
            'churn_metrics': {
                'high_risk_rate': round((feedback_df['Churn_Risk'] == 'High').mean() * 100, 1),
                'low_risk_rate': round((feedback_df['Churn_Risk'] == 'Low').mean() * 100, 1)
            },
            'operational_metrics': {
                'avg_response_time': round(feedback_df['Response_Time_Hours'].mean(), 1),
                'resolution_rate': round(feedback_df['Resolved'].mean() * 100, 1),
                'feedback_volume': len(feedback_df)
            },
            'sales_metrics': {
                'total_pipeline': round(deals_df[deals_df['Stage'].isin(['Prospecting', 'Qualification', 'Proposal', 'Negotiation'])]['Deal_Size'].sum(), 0),
                'avg_deal_size': round(deals_df['Deal_Size'].mean(), 0),
                'win_rate': round((deals_df['Stage'] == 'Closed Won').mean() * 100, 1) if len(deals_df) > 0 else 0
            }
        }
        
        return metrics

    def _get_segment_recommendation(self, segment, metrics):
        """Get recommendation for specific segment"""
        if metrics['Sentiment_Score'] < -0.2:
            return f"High priority: Address satisfaction issues in {segment} segment"
        elif metrics['Churn_Risk'] > 5:
            return f"Focus on churn prevention for {segment} customers"
        elif metrics['Response_Time_Hours'] > 24:
            return f"Improve response times for {segment} segment"
        else:
            return f"Maintain current service levels for {segment} segment"

    def _get_regional_recommendation(self, region, metrics):
        """Get recommendation for specific region"""
        if metrics['Sentiment_Score'] < -0.2:
            return f"Deploy additional resources to improve {region} satisfaction"
        elif metrics['Churn_Risk'] > 5:
            return f"Implement retention program in {region}"
        elif metrics['Response_Time_Hours'] > 24:
            return f"Strengthen support coverage in {region}"
        else:
            return f"Leverage {region} best practices for other regions"

    def _get_pain_point_recommendations(self, pain_point_counts):
        """Get recommendations based on pain point analysis"""
        recommendations = []
        
        top_pain_points = pain_point_counts.most_common(3)
        for pain_point, count in top_pain_points:
            if pain_point in ['slow', 'response']:
                recommendations.append("Implement faster response time SLAs")
            elif pain_point in ['expensive', 'pricing']:
                recommendations.append("Review pricing strategy and value communication")
            elif pain_point in ['support', 'help']:
                recommendations.append("Enhance customer support training and resources")
            elif pain_point in ['difficult', 'complicated']:
                recommendations.append("Simplify user experience and improve documentation")
            elif pain_point in ['integration', 'technical']:
                recommendations.append("Improve technical documentation and integration support")
            else:
                recommendations.append(f"Address '{pain_point}' issues through targeted improvement program")
        
        return recommendations
