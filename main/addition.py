class Person:

    def __init__(self, name, gender, age, email):
        self.name = name
        self.gender = gender
        self.age = age
        self.email = email

    def __str__(self):
        return f'Имя: {self.name}, Пол: {self.gender}, Возраст: {self.age}, Электронная почта: {self.email}'

    def __repr__(self):
        return f'description: {str(self)} repr: {super().__repr__()}'
