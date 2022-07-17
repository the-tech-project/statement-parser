from StatementParser import StatementParser

statement = StatementParser('./HDFC Financial Year 2021-2022.pdf', 'HDFC')

statement.get_opening_balance()
statement.get_transactions()
statement.get_credits()
statement.get_debits()
statement.get_closing_balance()

statement.to_list()
