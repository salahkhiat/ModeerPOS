class Student:
    def __init__(self, name):
        self._name = name 
        self.count = 0
        print(f"initializing ...")


    def __enter__(self):
        print(f"{self._name} Class is ready")

    def __next__(self):
        self.count += 1

    def __exit__(self, exc_type, exc, tb):
        print(f"count number {self.count}")
        print("good bay.")

a = Student("Ahmed")
with a:
    print("processing ...")

with a:
    print("processing 2...")