"""Code execution engine for Micro Plutoscope."""
import sys
from io import StringIO
from ._base import SingletonMeta


class CodeExecutor(metaclass=SingletonMeta):
    """Executes code and captures output. Singleton pattern - only one instance."""
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the CodeExecutor.
        
        Args:
            timeout: Maximum execution time in seconds (default 30)
        """
        # Only initialize once
        if not hasattr(self, '_initialized'):
            self.timeout = timeout
            self.output = ""
            self.error = ""
            self.success = False
            self._initialized = True
    
    def execute_python(self, code: str) -> str:
        """
        Execute Python code and capture output.
        
        Args:
            code: Python code string to execute
            
        Returns:
            Output from the executed code
        """
        try:
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            # Execute the code with safe namespace
            namespace = {}
            exec(code, namespace)
            
            # Get the output
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # If no output was captured, show success message
            if not output.strip():
                output = "Code executed successfully (no output)"
            
            self.output = output
            self.error = ""
            self.success = True
            return output
        except Exception as e:
            sys.stdout = old_stdout
            self.error = str(e)
            self.success = False
            return f"Error: {str(e)}"
    
    def execute_sql(self, code: str, db_string: str) -> str:
        """
        Execute SQL code against PostgreSQL and capture output.
        
        Args:
            code: SQL code string to execute
            db_string: PostgreSQL connection string (e.g., postgresql://user:pass@localhost/dbname)
            
        Returns:
            Output from the executed SQL
        """
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            conn = psycopg2.connect(db_string)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(code)
            conn.commit()
            
            # Fetch results if it's a SELECT query
            if code.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                output = "\n".join([str(dict(row)) for row in results])
            else:
                output = f"Query executed successfully. Rows affected: {cursor.rowcount}"
            
            cursor.close()
            conn.close()
            self.output = output
            self.error = ""
            self.success = True
            return output
                
        except Exception as e:
            self.error = str(e)
            self.success = False
            return f"Error: {str(e)}"
    
    def __call__(self, code: str, language: str = "python") -> str:
        """
        Execute code based on language.
        
        Args:
            code: Code string to execute
            language: Programming language ("python", "sql")
            
        Returns:
            Output from the executed code
        """
        language = language.lower()
        
        if language == "python":
            return self.execute_python(code)
        elif language == "sql":
            # SQL execution requires db_string - not supported without connection string
            self.error = "SQL execution requires a database connection string"
            self.success = False
            return f"Error: {self.error}"
        else:
            self.error = f"Unsupported language: {language}"
            self.success = False
            return f"Error: {self.error}"
    
    # Class-level access methods
    @classmethod
    def python(cls, code: str) -> str:
        """Execute Python code via class method."""
        return cls().execute_python(code)
    
    @classmethod
    def sql(cls, code: str, db_string: str) -> str:
        """Execute SQL code via class method."""
        return cls().execute_sql(code, db_string)
    
    @classmethod
    def run(cls, code: str, language: str = "python") -> str:
        """Run code via class method."""
        return cls()(code, language)