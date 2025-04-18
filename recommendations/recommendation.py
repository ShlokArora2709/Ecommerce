# recommendations/recommendation_model.py
import numpy as np
from sklearn.decomposition import NMF
from products.models import Product
from recommendations.models import UserProductInteraction
import pandas as pd
from django.db import models
class RecommendationModel:
    def __init__(self, n_factors=20):
        self.n_factors = n_factors
        self.model = NMF(n_components=n_factors, init='random', random_state=42)
        self.user_factors = None
        self.item_factors = None
        self.user_mapping = {}
        self.item_mapping = {}
        self.reverse_user_mapping = {}
        self.reverse_item_mapping = {}
        
    def _create_interaction_matrix(self):
        # Get all interactions
        interactions = UserProductInteraction.objects.all().values('user_id', 'product_id', 'view_count', 'purchased', 'liked')
        df = pd.DataFrame(list(interactions))
        if df.empty:
            return np.zeros((1, 1)), {}, {}
        
        # Create user and item mappings
        unique_users = df['user_id'].unique()
        unique_items = df['product_id'].unique()
        
        user_mapping = {user_id: idx for idx, user_id in enumerate(unique_users)}
        item_mapping = {item_id: idx for idx, item_id in enumerate(unique_items)}
        
        # Create reverse mappings
        reverse_user_mapping = {idx: user_id for user_id, idx in user_mapping.items()}
        reverse_item_mapping = {idx: item_id for item_id, idx in item_mapping.items()}
        
        # Create interaction matrix (with a weighted score)
        matrix = np.zeros((len(user_mapping), len(item_mapping)))
        
        for _, row in df.iterrows():
            u_idx = user_mapping[row['user_id']]
            i_idx = item_mapping[row['product_id']]
            
            # Calculate a score based on interactions
            score = 0
            
            score += min(row['view_count'], 5) * 0.2 
            if row['purchased']:
                score += 1.0  
            if row['liked']:
                score += 0.5 
                
            matrix[u_idx, i_idx] = score
            
        return matrix, user_mapping, item_mapping, reverse_user_mapping, reverse_item_mapping
    
    def train(self):
        matrix, self.user_mapping, self.item_mapping, self.reverse_user_mapping, self.reverse_item_mapping = self._create_interaction_matrix()
        if matrix.shape[0] == 1 and matrix.shape[1] == 1 and matrix[0, 0] == 0:
            return

        if matrix.shape[0] < 2 or matrix.shape[1] < 2:
            return
            
        # Train the model
        self.user_factors = self.model.fit_transform(matrix)
        self.item_factors = self.model.components_.T
        
    def get_recommendations(self, user_id, top_n=5):
        from recommendations.cython_utils import fast_recommendations
        
        if self.user_factors is None:
            random_products = Product.objects.order_by('?')[:top_n]
            return list(random_products)
        
        # Check if user is in the mapping
        if user_id not in self.user_mapping:
            # New user, return popular products
            popular_products = Product.objects.annotate(
                interaction_count=models.Count('userproductinteraction')
            ).order_by('-interaction_count')[:top_n]
            return list(popular_products)
        
        user_idx = self.user_mapping[user_id]
        user_vector = self.user_factors[user_idx]
        
        recommendations = fast_recommendations(
            user_vector, 
            self.item_factors, 
            top_n,
            [self.reverse_item_mapping[i] for i in range(len(self.reverse_item_mapping))]
        )
        
        # Convert product ids to Product objects
        product_ids = [rec[0] for rec in recommendations]
        recommended_products = list(Product.objects.filter(id__in=product_ids))
        
        # Sort products in the order of recommendation scores
        product_dict = {p.id: p for p in recommended_products}
        sorted_products = [product_dict[pid] for pid in product_ids if pid in product_dict]
        
        return sorted_products