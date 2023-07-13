# MLOps Homework

- [Code Philosophy](#code-philosophy)
- [Homework Structure](#homework-structure)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
- [Problem](#problem)
  - [Part 1](#part-1)
  - [Part 2](#part-2)
  - [Part 3](#part-3)

## Code Philosophy

At Vinted, we strive to write clean and simple code, covered with unit tests,
and easy to maintain. We also put a high value on consistency and following the
[language code style](https://google.github.io/styleguide/pyguide.html). We
expect to see the same values conveyed in the problem solution.

## Homework Structure

The homework is split into three parts, each of which will be described in more
detail below. You are free to choose which parts you want to solve - make this
decision based on how comfortable you feel with the problems presented in each
part. Of course, solving as many parts as you can will let us get a better
understanding of your skills. It's not required to solve the parts in order,
but some parts do depend on each other (e.g. you can choose to solve only parts
1 and 3, but you can't solve part 2 without first solving part 1).

Each part (except the last one) is already covered with automated tests. You
are **not** allowed to modify these tests, but you **are** welcome to add more
tests if you feel like they would help. To consider a part solved, all of its
pre-added tests must pass.

You can run the tests using the command `python -m pytest`. To run the tests
for a specific part, add the command line argument `-m partX`. For example, to
run the tests for part 1, use the command `python -m pytest -m part1`.

## Requirements

* The solution should be implemented using the Python programming language.
* Your solution should match the philosophy described above.
* Using additional libraries (except the ones that are already added for you)
  is prohibited. You can use the standard Python library.
* A short documentation of design decisions and assumptions can be provided in
  the code itself.
* Your design should be flexible enough to allow adding new rules or endpoints
  and modifying existing ones easily.

## Getting Started

* Install Python 3.7+
* Create a virtual environment and activate it:

  ```bash
  python -m venv venv
  source venv/bin/activate
  ```

* Install the required dependencies:
  
  ```bash
  pip install -r requirements.txt
  ```

## Problem

Here, at Vinted, our members call themselves 'Vinties' and shopping at Vinted
even has its own term - 'to vint'. And our members do vint a lot. Naturally,
when something is purchased, it has to be shipped and Vinted provides various
shipping options to its members across the globe. However, let's focus on
France. In France, it is allowed to ship via either 'Mondial Relay' (MR in
short) or 'La Poste' (code LP). While 'La Poste' provides usual courier delivery
services, 'Mondial Relay' allows you to drop and pick up a shipment at a
so-called drop-off point, thus being less convenient, but cheaper for larger
packages.

Each item, depending on its size gets an appropriate package size assigned to
it:

* S - Small, a popular option to ship jewelry
* M - Medium - clothes and similar items
* L - Large - mostly shoes

Shipping price depends on package size and a carrier:

| Carrier code | Package Size | Price  |
| ------------ | ------------ | ------ |
| LP           | S            | 1.50 € |
| LP           | M            | 4.90 € |
| LP           | L            | 6.90 € |
| MR           | S            | 2 €    |
| MR           | M            | 3 €    |
| MR           | L            | 4 €    |

Usually, the shipping price is covered by the buyer, but sometimes, in order to
promote one or another carrier, Vinted covers part of the shipping price.

### Part 1

Your task is to implement the `TransactionProcessor` class in
`shipping/transactions.py`. This class should be able to process transactions
one-by-one and calculate the shipping price and discount for each of them.

Transactions will be passed to the `process_transaction` method of the
`TransactionProcessor` class. The transactions will be provided as a dictionary
of shape
`{"date": "YYYY-MM-DD", "carrier": "string", "package_size": "string"}`. The
method is expected to return a dictionary of shape
`{"reduced_price": price, "applied_discount": price or None}`. For better understanding
of the contract, feel free to check out the tests.

To calculate the discounts, implement the following rules:

1. All S shipments should always match the lowest S package price among the
   providers.
2. Every third L shipment via LP (counted regardless of the month) should be free, but the discount applies only once a calendar month.
3. Accumulated discounts cannot exceed 10 € in a calendar month. If there are
   not enough funds to fully cover a discount this calendar month, it should be
   covered partially.

**Your design should be flexible enough to allow adding new rules and modifying existing ones easily.**

### Part 2

This part depends on part 1.

Once your shipping price calculation logic works as expected, your next task is
to build a service that can be used to perform these calculations. To do this,
you should implement a REST API using [FastAPI](https://fastapi.tiangolo.com/).

To start off, implement a `POST /transactions` endpoint that accepts incoming
transactions and calculates the shipping prices and discounts for them
one-by-one. The endpoint should accept a transaction via the request body. The
body should be a JSON object with the following shape:

```json
{
  "date": "string",
  "package_size": "string",
  "carrier": "string"
}
```

The endpoint should respond a JSON object with the following shape:

```json
{
  "reduced_price": "string",
  "applied_discount": "string or null"
}
```

The prices should be returned as strings and must have *exactly* two digits
after the decimal point.

Next, we noticed that the transaction functionality is only valid since 2010.
To make sure that our service can't be corrupted by older transactions,
implement validation logic to reject old transactions: if a transaction with
a date earlier than 2010-01-01 comes in, the service should respond with HTTP
code 422 and the response message should include the text
*"Transactions older than 2010 are not supported"*.

Finally, it's not very nice that the list of shipping providers in our service
is static - making it configurable would be much better. To start off, the team
decided to implement the necessary functionality to enable or disable existing
shipping providers - adding or removing shipping providers will be done some
time in the future.

To implement this feature, you need your service to expose two new endpoints -
`GET /carriers` and `POST /carriers`. Each carrier should be a JSON object
with the following shape:

```json
{
  "carrier": "string",
  "enabled": "boolean"
}
```

The `GET /carriers` endpoint should return a response that contains the current
configuration of the carriers:

```json
{
  "carriers": [
    {
      "carrier": "string",
      "enabled": "boolean"
    }
  ]
}
```

The `POST /carriers` endpoint can be used to to configure *existing* carriers
by either enabling or disabling them. The endpoint should accept a carrier
object via request body and update the service's internal state. If the carrier
code provided in the request body is invalid (i.e. it doesn't exist in the
current configuration), the service should respond with HTTP code 422.

The previously implemented `POST /transactions` endpoint should now take into
account the current carrier configuration. If a transaction using a disabled
carrier comes in, the service should respond with HTTP code 422 and the
response body should include the message *"Carrier with code 'X' is disabled"*
where *"X"* is the carrier code provided in the request body.

### Part 3

In order to be able to perform different analyses on the historical data of
orders, an archive of all processed orders is stored somewhere in our data
centers. For simplicity, let's assume all orders are stored in a simple text
file, one line per order. The format of each line is as follows:

```text
date packge_size carrier
```

The `date` is stored in ISO format (`YYYY-MM-DD`), the package size is exactly
one letter - either "S", "M" or "L", and the carrier is one of "LP" and "MR".
All strings are case insensitive (e.g. "m" would be a valid package size).

For example, here are the contents of one valid archive file:

```text
2015-02-01 S MR
2015-02-02 S MR
2015-02-03 L LP
2015-02-05 S LP
2015-02-06 S MR
2015-02-06 L LP
2015-02-07 L MR
```

Unfortunately, these rules only describe what the archive file *should* look
like. In reality, some of the data in it can be corrupted - the date could be
in the wrong format, the carrier code might be invalid, etc.

Additionally, some people in Vinted want to generate some insights from the
data. They're interested to know how many orders have been placed on each day
and the maximum number of orders placed per day.

The task this time is to write a script that would analyze a given archive file
and report any errors that it finds. This time, however, you don't have to
implement the script yourself - a member of your team has already done it and
pushed their changes to a branch. Therefore, your actual task for this part of
the homework is to perform a code review and leave any feedback you can come
up with.

Due to the technical limitations of Github classrooms, you need to run the
following git commands after checking out the repository (to refresh git
history):

```bash
git checkout origin/toreview -b toreview
git rebase -Xtheirs main
git push -f
```

Then, open a pull request from the branch `toreview` to the `main` branch. Once
your pull request is open, you can imagine that it was actually opened by your
colleague and proceed with the code review process.