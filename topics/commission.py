from .base import Topic

class CommissionTopic(Topic):
    def __init__(self, name, customer, employee):
        super().__init__(name)
        self.customer = customer
        self.employee = employee
        super().add_member(customer)
        super().add_member(employee)