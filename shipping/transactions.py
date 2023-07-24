from decimal import Decimal


class ShippingPrice:
    def __init__(self, carrier, package_size, price):
        self.carrier = carrier
        self.package_size = package_size
        self.price = price


class Carrier:
    def __init__(self, name, shipping_prices):
        self.name = name
        self.shipping_prices = shipping_prices
        self.enabled = True

    def get_shipping_price(self, package_size):
        return self.shipping_prices.get(package_size)

    def to_json(self):
        return {"code": self.name, "enabled": self.enabled}


class MonthData:
    def __init__(self):
        self.total_discount = 0
        self.lp_l_shipments_discount = False


class TransactionProcessor:

    def __init__(self):

        self.all_month_data = {}  # MonthData objects by month
        self.lp_l_shipments_count = 0
        self.shipping_carriers = []
        self.shipping_carriers.append(Carrier("LP", {"S": Decimal("1.50"), "M": Decimal("4.90"), "L": Decimal("6.90")}))
        self.shipping_carriers.append(Carrier("MR", {"S": Decimal("2.00"), "M": Decimal("3.00"), "L": Decimal("4.00")}))

    def is_carrier_enabled(self, carrier):
        # check if carrier is enabled
        for shipping_carrier in self.shipping_carriers:
            if shipping_carrier.name == carrier:
                return shipping_carrier.enabled
        return False

    def get_carrier(self, carrier):
        # get carrier from self.shipping_carriers
        for shipping_carrier in self.shipping_carriers:
            if shipping_carrier.name == carrier:
                return shipping_carrier
        return None

    def get_carriers(self):
        # get all carriers
        return self.shipping_carriers

    def get_shipping_price(self, carrier, package_size):
        # get shipping price from self.shipping_carriers

        for shipping_carrier in self.shipping_carriers:
            if shipping_carrier.name == carrier and shipping_carrier.enabled:
                return shipping_carrier.get_shipping_price(package_size)

        raise ValueError(f"Price for carrier {carrier} with package size {package_size} not found")

    def get_lowest_s_price(self):
        # get lowest S price from self.shipping_carriers
        lowest_s_price = None
        for shipping_carrier in self.shipping_carriers:
            if shipping_carrier.enabled:
                s_price = shipping_carrier.get_shipping_price("S")
                if lowest_s_price is None or s_price < lowest_s_price:
                    lowest_s_price = s_price

        if lowest_s_price is None:
            raise ValueError("No shipping price for S package size found")

        return lowest_s_price

    def get_month_data(self, month):
        # get month data from self.all_month_data or create if not exists
        if month not in self.all_month_data:
            self.all_month_data[month] = MonthData()
        return self.all_month_data[month]

    def calculate_discount(self, carrier, package_size, shipping_price, month_data):
        # calculate discount and update month_data
        remaining_discount = Decimal("10.00") - month_data.total_discount

        if remaining_discount <= 0:
            return None

        # LP L discount
        if package_size == "L" and carrier == "LP":
            self.lp_l_shipments_count += 1
            if self.lp_l_shipments_count % 3 == 0 and not month_data.lp_l_shipments_discount:
                month_data.lp_l_shipments_discount = True
                if remaining_discount >= shipping_price:
                    month_data.total_discount += shipping_price
                    return shipping_price
                else:
                    month_data.total_discount += remaining_discount
                    return remaining_discount

        # Small package discount
        if package_size == "S":
            # smallest S price from all carriers
            smallest_s_price = self.get_lowest_s_price()
            suggested_discount = shipping_price - smallest_s_price
            if suggested_discount:
                if remaining_discount >= suggested_discount:
                    month_data.total_discount += suggested_discount
                    return suggested_discount
                else:
                    month_data.total_discount += remaining_discount
                    return remaining_discount

        # no discount
        return None

    def process_transaction(self, transaction):

        carrier = transaction["carrier"]
        package_size = transaction["package_size"]

        transaction_date = transaction["date"]
        transaction_month = transaction_date[:7]
        month_data = self.get_month_data(transaction_month)
        shipping_price = self.get_shipping_price(carrier, package_size)
        discount = self.calculate_discount(carrier, package_size, shipping_price, month_data)

        if discount is None:
            return {"reduced_price": shipping_price, "applied_discount": discount}
        else:
            return {"reduced_price": shipping_price - discount, "applied_discount": discount}


transaction_processor = TransactionProcessor()
