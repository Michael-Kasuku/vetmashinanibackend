import os
import pickle
import numpy as np
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from bs4 import BeautifulSoup

@csrf_exempt
def predict_disease(request):
    if request.method == 'POST':
        try:
            data = request.POST.getlist('symptoms[]')  # Expecting a list of symptoms
            
            model_file = os.path.join(settings.BASE_DIR, 'diagnosis/model.pkl')
            if not os.path.exists(model_file):
                return JsonResponse({"error": "Model file not found"}, status=500)
            
            with open(model_file, 'rb') as f:
                model, scaler, feature_columns, disease_mapping = pickle.load(f)

            input_data = np.zeros(len(feature_columns))
            for symptom in data:
                if symptom in feature_columns:
                    input_data[feature_columns.index(symptom)] = 1

            input_data = scaler.transform([input_data])
            prediction = model.predict(input_data)
            disease_name = {v: k for k, v in disease_mapping.items()}[prediction[0]]

            return JsonResponse({"predicted_disease": disease_name})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

# AVL Tree Node
class AVLTreeNode:
    def __init__(self, title, url):
        self.title = title
        self.url = url
        self.left = None
        self.right = None
        self.height = 1  # Height of node for balancing

class AVLTree:
    def __init__(self):
        self.root = None

    def insert(self, title, url):
        """Inserts a new node in the tree and balances the tree."""
        self.root = self._insert(self.root, title, url)

    def _insert(self, node, title, url):
        """Recursive insert helper function."""
        if not node:
            return AVLTreeNode(title, url)
        
        if title < node.title:
            node.left = self._insert(node.left, title, url)
        else:
            node.right = self._insert(node.right, title, url)

        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)

        if balance > 1 and title < node.left.title:
            return self._rotate_right(node)
        if balance < -1 and title > node.right.title:
            return self._rotate_left(node)
        if balance > 1 and title > node.left.title:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1 and title < node.right.title:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _rotate_left(self, z):
        """Performs a left rotation."""
        if z is None or z.right is None:
            return z
        
        y = z.right
        T2 = y.left

        y.left = z
        z.right = T2

        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))

        return y

    def _rotate_right(self, z):
        """Performs a right rotation."""
        if z is None or z.left is None:
            return z
        
        y = z.left
        T3 = y.right

        y.right = z
        z.left = T3

        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))

        return y

    def _get_height(self, node):
        """Returns the height of the node."""
        return 0 if not node else node.height

    def _get_balance(self, node):
        """Returns the balance factor of the node."""
        return 0 if not node else self._get_height(node.left) - self._get_height(node.right)

    def inorder_traversal(self):
        """Performs an in-order traversal of the tree and returns the results."""
        results = []
        self._inorder_recursive(self.root, results)
        return results

    def _inorder_recursive(self, node, results):
        """Recursive in-order traversal."""
        if node:
            self._inorder_recursive(node.left, results)
            results.append({'title': node.title, 'url': node.url})
            self._inorder_recursive(node.right, results)

# URLs to fetch data from
urls = [
    "https://www.scholars4dev.com/",
    "https://www.idealist.org/",
    "https://www.internships.com/",
    "https://www.craigslist.org/",
    "https://www.usajobs.gov/",
    "https://www.hirepurpose.com/",
    "https://www.wayup.com/",
    "https://www.linkedin.com/jobs/",
    "https://www.jobvite.com/",
    "https://www.naukri.com/",
    "https://www.careers360.com/",
    "https://www.scholarlyoa.com/",
    "https://www.acs.org/content/acs/en/careers.html",
    "https://www.job.com/",
]

def fetch_grants_and_jobs(url, search_phrase):
    """Fetch and parse grants, jobs, internships, scholarships from the provided URL based on a search phrase."""
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = soup.find_all('a', href=True)
        
        results = []
        
        for link in links:
            title = link.get_text(strip=True)
            href = link['href']
            if search_phrase in title.lower() or search_phrase in href.lower():
                results.append({'title': title, 'url': href})
        
        return results

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

@csrf_exempt
def job_vibe(request):
    """Django view to fetch job, internship, scholarship, and grant opportunities."""
    
    search_phrase = request.GET.get('search_phrase', '').strip().lower()
    
    if not search_phrase:
        return JsonResponse({'error': 'Search phrase cannot be empty!'}, status=400)
    
    avl_tree = AVLTree()
    
    for url in urls:
        results = fetch_grants_and_jobs(url, search_phrase)
        for result in results:
            avl_tree.insert(result['title'], result['url'])
    
    all_results = avl_tree.inorder_traversal()
    
    if all_results:
        return JsonResponse({'results': all_results}, status=200)
    else:
        return JsonResponse({'message': 'No relevant opportunities found.'}, status=404)
