from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Load environment variables from .env file
load_dotenv()

from auth import router as auth_router
from models import init_db
from student_routes import router as student_router
from teacher_routes import router as teacher_router

app = FastAPI(title="Adaptive Learning System")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _populate_default_flows():
    """Populate default learning flows on startup if database is empty."""
    from models import create_flow, create_question
    import json
    
    TEACHER_EMAIL = "jnpriyanshipragya@gmail.com"
    
    flows_data = [
        {
            "title": "Data Structures Fundamentals",
            "questions": [
                ("What is an array?", "A contiguous block of memory storing elements of the same type", ["A collection of unique elements", "A recursive data structure", "A tree-like structure"], "1", "Think about how memory is allocated for a list of items."),
                ("Array access time complexity?", "O(1) - Constant time", ["O(n) - Linear time", "O(log n) - Logarithmic time", "O(n²) - Quadratic time"], "1", "Since arrays store elements in contiguous memory, accessing by index is direct."),
                ("What is a linked list?", "A data structure where elements are stored in nodes, with each node containing a reference to the next node", ["A contiguous block of memory", "A tree structure with multiple children", "A hash table"], "2", "Think about a chain where each link points to the next one."),
                ("Linked list insertion at beginning?", "O(1) - Constant time", ["O(n) - Linear time", "O(log n) - Logarithmic time", "O(n²) - Quadratic time"], "2", "You only need to update pointers, not shift any elements."),
                ("What is a stack?", "A LIFO (Last In, First Out) data structure where elements are added and removed from the same end", ["A FIFO structure", "A randomly accessible data structure", "Multiple levels of depth"], "2", "Think of a stack of plates - you add and remove from the top."),
                ("Binary tree space complexity?", "O(n) - Linear space", ["O(log n) - Logarithmic space", "O(1) - Constant space", "O(n²) - Quadratic space"], "3", "Each node requires storage, and there are n nodes total."),
                ("Balanced BST search complexity?", "O(log n) - Logarithmic time", ["O(1) - Constant time", "O(n) - Linear time", "O(n log n)"], "3", "Each comparison eliminates half the search space."),
                ("LRU cache data structure?", "Combination of HashMap and Doubly Linked List", ["Only an array", "Only a stack", "Only a queue"], "3", "You need fast lookup and ability to track insertion/access order."),
            ]
        },
        {
            "title": "Algorithms: Sorting",
            "questions": [
                ("Bubble Sort time complexity?", "O(n²) in worst and average case", ["O(n)", "O(n log n)", "O(1)"], "1", "Bubble sort compares adjacent elements repeatedly."),
                ("Merge Sort time complexity?", "O(n log n) in all cases", ["O(n²)", "O(n)", "O(2^n)"], "2", "Merge sort divides the array and conquers by merging."),
                ("Which sort is stable?", "Merge Sort and Insertion Sort", ["Quick Sort only", "Heap Sort only", "Bubble Sort never"], "2", "Stable sorts preserve the relative order of equal elements."),
                ("Quick Sort worst case?", "O(n²) when pivot is always smallest/largest", ["O(n log n)", "O(n)", "O(log n)"], "2", "This happens with already sorted arrays and bad pivot selection."),
                ("Heap Sort space complexity?", "O(1) - In-place sorting", ["O(n)", "O(log n)", "O(n log n)"], "3", "Heap sort doesn't require extra space beyond input."),
                ("Counting Sort time complexity?", "O(n + k) where k is range of input", ["O(n log n)", "O(n²)", "O(k)"], "3", "Counting sort is not comparison-based and works for integers."),
                ("Radix Sort time complexity?", "O(d * (n + k)) where d is number of digits", ["O(n log n)", "O(n²)", "O(n)"], "3", "Radix sort processes numbers digit by digit."),
                ("Which sort has best cache locality?", "Insertion Sort", ["Quick Sort", "Merge Sort", "Heap Sort"], "3", "Insertion sort accesses nearby memory locations."),
            ]
        },
        {
            "title": "Searching Algorithms",
            "questions": [
                ("Linear Search time complexity?", "O(n) in all cases", ["O(log n)", "O(1)", "O(n²)"], "1", "Linear search checks each element one by one."),
                ("Binary Search requirement?", "Array must be sorted", ["Array must have odd length", "All elements must be unique", "Array must be in descending order"], "1", "Binary search only works on sorted arrays."),
                ("Binary Search time complexity?", "O(log n)", ["O(n)", "O(1)", "O(n log n)"], "1", "Binary search halves the search space each time."),
                ("Depth-First Search use case?", "Finding path, detecting cycles, topological sort", ["Shortest path in unweighted graph", "Priority queue operations", "Finding median quickly"], "2", "DFS explores as far as possible along each branch."),
                ("Breadth-First Search use case?", "Shortest path in unweighted graph", ["Finding cycles in directed graphs", "Topological sorting", "Checking if tree is balanced"], "2", "BFS explores all neighbors before moving deeper."),
                ("BFS time complexity?", "O(V + E) where V is vertices, E is edges", ["O(V²)", "O(E²)", "O(log V)"], "2", "BFS visits each vertex and edge once."),
                ("Dijkstra's algorithm requirement?", "Non-negative edge weights", ["Directed graph only", "Connected graph only", "At most 1000 vertices"], "3", "Negative weights break Dijkstra's algorithm."),
                ("A* search heuristic property?", "Must be admissible (never overestimate)", ["Must always return optimal path", "Must process nodes in order", "Must use Manhattan distance"], "3", "Admissibility ensures A* finds optimal path."),
            ]
        },
        {
            "title": "Dynamic Programming Basics",
            "questions": [
                ("What is DP's main principle?", "Break problem into overlapping subproblems and store results", ["Always use recursion", "Avoid all loops", "Sort the data first"], "1", "Dynamic programming avoids redundant calculations."),
                ("Fibonacci DP time complexity?", "O(n) with memoization", ["O(2^n) with recursion", "O(n²)", "O(log n)"], "2", "DP reduces exponential recursion to linear time."),
                ("Optimal Substructure means?", "Optimal solution contains optimal solutions of subproblems", ["All subproblems must be independent", "Array must be sorted", "Problem must be linear"], "2", "This is a requirement for applying DP."),
                ("Knapsack 0/1 time complexity?", "O(n * W) where n is items, W is capacity", ["O(n²)", "O(n log n)", "O(2^n)"], "2", "Knapsack DP uses a 2D table."),
                ("Longest Common Subsequence approach?", "Compare characters and build DP table", ["Sort both strings first", "Use hash table", "Binary search approach"], "3", "LCS finds matching characters in order."),
                ("Edit Distance (Levenshtein)?", "Minimum operations: insert, delete, replace", ["Only counting differences", "Only character matching", "Sorting based"], "3", "Edit distance measures how different two strings are."),
                ("Coin Change greedy fails because?", "Greedy doesn't always give optimal for all denominations", ["It's too slow", "Coins must be sorted", "Impossible with large amounts"], "3", "Example: coins [1,3,4], amount 6 → DP beats greedy."),
                ("Matrix Chain Multiplication purpose?", "Find optimal order to multiply matrices efficiently", ["Sort matrix elements", "Invert matrices", "Find determinant"], "3", "Different parenthesization changes scalar multiplications."),
            ]
        },
        {
            "title": "Graph Theory Essentials",
            "questions": [
                ("What is a graph?", "Collection of vertices connected by edges", ["A sorted list of numbers", "A type of tree", "A matrix of data"], "1", "Graphs represent relationships between objects."),
                ("Directed vs Undirected graph?", "Directed has one-way edges, Undirected has two-way edges", ["Directed is faster", "Undirected requires more memory", "They're the same thing"], "1", "Direction matters in social networks like Twitter (follow)."),
                ("Graph representation method?", "Adjacency List or Adjacency Matrix", ["Linked List only", "Hash Set only", "Array only"], "2", "Both have different space and time trade-offs."),
                ("Cycle detection in undirected graph?", "Use DFS or BFS, detect if visited node is parent", ["Count edges > vertices", "All edges must be unique", "Node colors"], "2", "A cycle means we revisit a node without being parent."),
                ("Strongly Connected Component?", "All vertices reachable from any other vertex", ["Graph has no edges", "Tree structure only", "Complete graph only"], "3", "Used in finding circular dependencies."),
                ("Topological Sort requirement?", "Graph must be a DAG (Directed Acyclic Graph)", ["Must be connected", "Must be bipartite", "Must have cycles"], "3", "Cycles make topological sorting impossible."),
                ("Minimum Spanning Tree purpose?", "Connect all vertices with minimum total edge weight", ["Find shortest path", "Detect cycles", "Sort vertices"], "3", "MST is useful in network design."),
                ("Bipartite Graph definition?", "Vertices can be divided into 2 sets with no edges within sets", ["All vertices connected", "Only one edge per vertex", "Forms a cycle"], "3", "Used in matching problems and coloring."),
            ]
        },
        {
            "title": "Object-Oriented Programming",
            "questions": [
                ("What is OOP?", "Programming paradigm using objects and classes to model real-world entities", ["Only for Python", "Same as functional programming", "Procedural approach only"], "1", "OOP improves code organization and reusability."),
                ("Encapsulation principle?", "Hide internal details and expose only necessary interface", ["Make everything public", "Use global variables", "No data hiding"], "1", "Encapsulation protects object state."),
                ("Inheritance benefit?", "Code reuse and establishing hierarchical relationships", ["Faster execution", "Smaller file size", "Fewer variables"], "2", "Child classes inherit properties from parent."),
                ("Polymorphism type?", "Method Overriding (runtime) and Overloading (compile-time)", ["Only for loops", "Only in Python", "Same as inheritance"], "2", "Polymorphism allows methods to behave differently based on context."),
                ("Abstraction purpose?", "Show essential features and hide complexity", ["Make code faster", "Reduce memory", "Simplify variable names"], "2", "Abstract classes define interfaces for subclasses."),
                ("SOLID principle S means?", "Single Responsibility Principle - one class, one reason to change", ["System design", "Simplicity", "Security"], "3", "Each class should have a single job."),
                ("Composition vs Inheritance?", "Composition is 'has-a', Inheritance is 'is-a'", ["They're identical", "Inheritance is better always", "Composition uses interfaces"], "3", "Prefer composition for flexibility."),
                ("Design Pattern purpose?", "Reusable solutions to common programming problems", ["Required for all code", "Speeds up execution", "Reduces file size"], "3", "Patterns like Singleton, Factory, Observer solve recurring problems."),
            ]
        },
        {
            "title": "Database Fundamentals",
            "questions": [
                ("What is a database?", "Organized collection of structured data", ["A spreadsheet only", "Random data storage", "File system only"], "1", "Databases enable efficient data retrieval."),
                ("RDBMS definition?", "Relational Database Management System storing data in tables", ["Only for large companies", "Same as file storage", "Only for documents"], "1", "SQL databases use RDBMS model."),
                ("Primary Key purpose?", "Uniquely identify each row in a table", ["Speed up queries", "Reduce storage", "For sorting"], "1", "Primary keys ensure data integrity."),
                ("Foreign Key relationship?", "Link between primary key of one table and column of another", ["Duplicate data", "Index creation", "Backup mechanism"], "2", "Foreign keys maintain referential integrity."),
                ("Normalization benefit?", "Reduce data redundancy and improve data integrity", ["Faster queries always", "Smaller database size", "No need for backups"], "2", "Normalization follows rules like 1NF, 2NF, 3NF."),
                ("Index trade-off?", "Faster SELECT but slower INSERT/UPDATE/DELETE", ["Indexes make everything slower", "No space overhead", "Can't be deleted"], "3", "Choose which columns to index carefully."),
                ("ACID properties meaning?", "Atomicity, Consistency, Isolation, Durability - transaction guarantees", ["Just acronym", "Backup strategy", "Query types"], "3", "ACID ensures reliable database transactions."),
                ("NoSQL vs SQL?", "SQL is structured (tables), NoSQL is flexible (documents/key-value)", ["NoSQL is always faster", "SQL is deprecated", "They're identical"], "3", "Choose based on data structure needs."),
            ]
        },
        {
            "title": "Web Development Basics",
            "questions": [
                ("HTTP method GET purpose?", "Retrieve data from server without side effects", ["Modify server data", "Create sessions", "Delete resources"], "1", "GET requests are idempotent."),
                ("HTTP status 200 means?", "OK - Request successful", ["Bad Request", "Not Found", "Server Error"], "1", "Status codes indicate request result."),
                ("REST API principle?", "Stateless client-server communication using HTTP methods", ["Always use WebSockets", "Session-based only", "No standards needed"], "2", "REST uses GET, POST, PUT, DELETE for CRUD."),
                ("Authentication vs Authorization?", "Authentication verifies who you are, Authorization grants permissions", ["Same thing", "Auth is obsolete", "Only for passwords"], "2", "Auth happens first, then authz."),
                ("JWT token benefit?", "Stateless authentication without server-side sessions", ["Faster than cookies", "More secure always", "Smaller than sessions"], "3", "JWT contains encoded data that can be verified."),
                ("CORS purpose?", "Allow cross-origin requests safely between different domains", ["Prevent all requests", "Encrypt data", "Cache responses"], "3", "CORS headers control which origins can access API."),
                ("Load Balancing purpose?", "Distribute traffic across multiple servers", ["Reduce code size", "Improve security", "Save bandwidth only"], "3", "Load balancing improves scalability and reliability."),
                ("CDN benefit?", "Content Delivery Network caches content geographically closer to users", ["Reduces CPU", "Improves security", "Stores databases"], "3", "CDN speeds up content delivery worldwide."),
            ]
        },
        {
            "title": "System Design Principles",
            "questions": [
                ("Scalability definition?", "System's ability to handle growing amount of work", ["Making code faster", "Using less memory", "Prettier UI"], "1", "Scalability is critical for growing applications."),
                ("Horizontal vs Vertical scaling?", "Horizontal adds more machines, Vertical upgrades existing machine", ["They're the same", "Horizontal is always better", "Vertical impossible"], "2", "Horizontal scaling is more flexible."),
                ("CAP Theorem states?", "Can't have Consistency, Availability, and Partition Tolerance all 3", ["All systems must follow it", "Always pick Consistency", "Only for databases"], "2", "Systems choose 2 out of 3 properties."),
                ("Caching benefit?", "Reduce database queries and improve response time", ["Reduces storage only", "Always use cache", "Cache is permanent"], "2", "Cache invalidation is one of hardest problems."),
                ("Replication purpose?", "Create multiple copies for redundancy and fault tolerance", ["Slow down system", "Reduce consistency", "Only backup"], "3", "Replication improves availability."),
                ("Sharding approach?", "Divide data across multiple databases by key range", ["Combine databases", "Duplicate all data", "Only for NoSQL"], "3", "Sharding improves scalability for large datasets."),
                ("Message Queue benefit?", "Decouple services and handle asynchronous processing", ["Synchronize all calls", "Reduce latency always", "Store permanent data"], "3", "Queues like Kafka enable event-driven architecture."),
                ("Monitoring metric importance?", "Track latency, throughput, error rates to identify issues", ["Just count requests", "Monitor once a day", "Impossible to implement"], "3", "Proper monitoring enables proactive problem detection."),
            ]
        },
        {
            "title": "Security Fundamentals",
            "questions": [
                ("Encryption purpose?", "Convert plaintext to ciphertext to keep data confidential", ["Guarantee authenticity", "Reduce file size", "Speed up access"], "1", "Encryption protects sensitive information."),
                ("Symmetric vs Asymmetric encryption?", "Symmetric uses same key, Asymmetric uses public/private key pair", ["Same thing", "Asymmetric is outdated", "Only one exists"], "1", "Asymmetric enables secure key exchange."),
                ("Hashing property?", "One-way function producing fixed-size output, deterministic", ["Reversible to original", "Different output each time", "Stores original data"], "2", "Hashing is used for passwords and checksums."),
                ("SQL Injection attack?", "Inserting malicious SQL code into input fields", ["Database corruption", "Network attack", "Hardware failure"], "2", "Use parameterized queries to prevent SQL injection."),
                ("XSS (Cross-Site Scripting) attack?", "Injecting malicious scripts into web pages viewed by others", ["Server being hacked", "Network packet loss", "Hardware issue"], "2", "Sanitize user input to prevent XSS."),
                ("HTTPS vs HTTP?", "HTTPS adds TLS encryption layer for secure communication", ["Same thing", "HTTPS slower always", "Only for banking"], "3", "HTTPS protects data in transit."),
                ("OAuth 2.0 purpose?", "Secure authorization protocol for third-party applications", ["Password sharing alternative", "Replaces passwords", "Only for Google"], "3", "OAuth prevents sharing passwords with apps."),
                ("Rate Limiting purpose?", "Restrict number of requests from user/IP to prevent abuse", ["Speed up API", "Reduce storage", "Always allow all requests"], "3", "Rate limiting protects against DoS attacks."),
            ]
        }
    ]
    
    for flow_data in flows_data:
        try:
            flow = create_flow(title=flow_data["title"], created_by=TEACHER_EMAIL)
            for q_data in flow_data["questions"]:
                content, correct, incorrect, difficulty, hint = q_data
                options = [correct] + incorrect
                create_question(
                    flow_id=flow.flow_id,
                    difficulty=difficulty,
                    question_text=content,
                    options=options,
                    correct_answer=correct,
                    hint_text=hint,
                )
            print(f"✓ Created flow: {flow_data['title']}")
        except Exception as e:
            print(f"✗ Error creating flow {flow_data['title']}: {e}")


@app.on_event("startup")
def _startup():
    init_db()
    # Populate default flows if none exist
    from models import list_flows, create_flow, create_question
    if not list_flows():
        print("Populating default learning flows...")
        _populate_default_flows()

app.include_router(auth_router)
app.include_router(teacher_router)
app.include_router(student_router)


@app.get("/")
def root(request: Request):
    accept = request.headers.get("accept") or ""
    if "text/html" in accept:
        return templates.TemplateResponse(
            "home.html",
            {
                "request": request,
                "page_title": "Adaptive Learning POC",
                "subtitle": "Login to continue as teacher or student.",
                "role": None,
                "user_email": None,
            },
        )
    return {"status": "Adaptive Learning POC running"}
