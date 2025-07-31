#!/usr/bin/env python3
"""
Sample application with intentional bugs for demonstration
"""
import os
import pickle
import hashlib
import time
import secrets
from typing import List, Dict, Any

# Simulated bcrypt for demonstration (in real code, use actual bcrypt)
class SimulatedBcrypt:
    @staticmethod
    def gensalt():
        return secrets.token_bytes(16)
    
    @staticmethod
    def hashpw(password: bytes, salt: bytes) -> bytes:
        # Simplified hash simulation (use real bcrypt in production!)
        return hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
    
    @staticmethod
    def checkpw(password: bytes, hashed: bytes) -> bool:
        # Extract salt from the first 16 bytes
        salt = hashed[:16] if len(hashed) >= 16 else b'defaultsalt'
        return hashlib.pbkdf2_hmac('sha256', password, salt, 100000) == hashed[16:]

bcrypt = SimulatedBcrypt()

class UserManager:
    def __init__(self):
        self.users = {}
        self.session_tokens = {}
    
    def create_user(self, username: str, password: str, email: str) -> bool:
        """Create a new user account"""
        # Fixed Bug 1: Now properly hashing passwords with bcrypt
        if username in self.users:
            return False
        
        # Hash password with salt using bcrypt (industry standard)
        salt = bcrypt.gensalt()
        password_hash = salt + bcrypt.hashpw(password.encode('utf-8'), salt)
        
        self.users[username] = {
            'password_hash': password_hash,  # Store hash, not plain text
            'email': email,
            'created_at': time.time()
        }
        return True
    
    def authenticate(self, username: str, password: str) -> str:
        """Authenticate user and return session token"""
        if username not in self.users:
            return None
        
        # Fixed Bug 1 continued: Secure password verification with bcrypt
        stored_hash = self.users[username]['password_hash']
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            # Use cryptographically secure random token generation
            token = secrets.token_urlsafe(32)  # 256-bit token
            self.session_tokens[token] = username
            return token
        return None

class DataProcessor:
    def __init__(self):
        self.cache = {}
    
    def process_numbers(self, numbers: List[int]) -> Dict[str, Any]:
        """Process a list of numbers and return statistics"""
        if not numbers:
            return {}
        
        # Fixed Bug 2: Handle edge cases for variance calculation
        total = sum(numbers)
        average = total / len(numbers)
        
        # Handle single element case (variance undefined for n=1)
        if len(numbers) == 1:
            return {
                'total': total,
                'average': average,
                'variance': None,  # Mathematically undefined for single value
                'count': len(numbers)
            }
        
        # Safe variance calculation for n > 1
        variance_sum = sum((x - average) ** 2 for x in numbers)
        variance = variance_sum / (len(numbers) - 1)  # Now safe: n-1 > 0
        
        return {
            'total': total,
            'average': average,
            'variance': variance,
            'count': len(numbers)
        }
    
    def expensive_calculation(self, data: List[int]) -> int:
        """Perform an efficient calculation with optimized performance"""
        # Fixed Bug 3: Optimized from O(n³) to O(n) complexity
        # The original algorithm was adding each element once when i==j==k
        # This is equivalent to just summing all elements in the array
        return sum(data)

class FileHandler:
    def save_data(self, data: Any, filename: str) -> bool:
        """Save data to file using pickle"""
        try:
            # Bug 4: Using pickle without validation (Security Vulnerability)
            with open(filename, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception:
            return False
    
    def load_data(self, filename: str) -> Any:
        """Load data from file using pickle"""
        try:
            # Bug 4 continued: Unsafe deserialization
            with open(filename, 'rb') as f:
                return pickle.load(f)  # Dangerous!
        except Exception:
            return None
    
    def read_user_file(self, filepath: str) -> str:
        """Read a user-specified file"""
        # Bug 5: Path traversal vulnerability (Security Issue)
        if not os.path.exists(filepath):
            return None
        
        # No validation of file path - allows ../../../etc/passwd
        with open(filepath, 'r') as f:
            return f.read()

def main():
    """Main function demonstrating the buggy code"""
    um = UserManager()
    dp = DataProcessor()
    fh = FileHandler()
    
    # Create some users
    um.create_user("admin", "password123", "admin@example.com")
    um.create_user("user1", "secret", "user1@example.com")
    
    # Authenticate
    token = um.authenticate("admin", "password123")
    print(f"Admin token: {token}")
    
    # Process some data
    numbers = [1, 2, 3, 4, 5]
    stats = dp.process_numbers(numbers)
    print(f"Stats: {stats}")
    
    # Bug demonstration: single number list
    single_num = [42]
    try:
        stats_single = dp.process_numbers(single_num)
        print(f"Single number stats: {stats_single}")
    except ZeroDivisionError as e:
        print(f"Error with single number: {e}")
    
    # Performance issue demonstration
    small_data = [1, 2, 3, 4, 5]
    result = dp.expensive_calculation(small_data)
    print(f"Expensive calculation result: {result}")
    
    # File operations
    test_data = {"key": "value", "numbers": [1, 2, 3]}
    fh.save_data(test_data, "test.pkl")
    loaded_data = fh.load_data("test.pkl")
    print(f"Loaded data: {loaded_data}")

if __name__ == "__main__":
    main()