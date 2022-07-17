###
# Bank statement parser base class.
###

from StatementParser.Banks.Base import Base
from gensim.utils import tokenize

import numpy
import pandas

class HDFC( Base ):

    def __init__(self, transactions):

        super().__init__()

        self.BANK = 'HDFC'
        self.HEADER = 'header'
        self.STATEMENT_END = 'statement_end'

        self.transactions = transactions;

        self.process()

    def process(self):
        self.combine_transaction()
        self.assign_transaction_type()
        self.to_dataframe()

    def assign_transaction_type(self):

        # initializing variables
        withdrawal = 'withdrawal'  # from BANK_DETAILS
        deposit = 'deposit'        # from BANK_DETAILS
        balance = 'balance'        # from BANK_DETAILS
        is_negative = False        # flag for default checking
        updated_transactions = []          # transactions with label assigned

        # iterate over all transactions
        for transaction in self.transactions:
            # debit leading to a negative balance
            if transaction[withdrawal] > 0 and transaction[balance] < 0:
                if is_negative:
                    # default condition not satisfied so move to debit
                    updated_transactions[-1]['type'] = 'Debit'

                is_negative = True
                transaction['type'] = 'Default'
                updated_transactions.append(transaction)

                # to avoid last statement of is_negative = False
                continue

            # followed by credit of same amount
            elif is_negative:
                # default condition met
                if transaction[deposit] == updated_transactions[-1]['withdrawal']:
                    transaction['type'] = 'Default'

                # default condition not met move to debit
                else:
                    updated_transactions[-1]['type'] = 'Debit'

                    # condition not satisfied
                    # now start over from current position
                    if transaction[withdrawal] > 0 and transaction[balance] < 0:
                        is_negative = True
                        transaction['type'] = 'Default'
                        updated_transactions.append(transaction)

                        continue

                    # debit
                    elif transaction[withdrawal] > 0:
                        transaction['type'] = 'Debit'

                    # credit
                    elif transaction[deposit] > 0:
                        transaction['type'] = 'Credit'

            # debit
            elif transaction[withdrawal] > 0:
                transaction['type'] = 'Debit'

            # credit
            elif transaction[deposit] > 0:
                transaction['type'] = 'Credit'

            is_negative = False
            updated_transactions.append(transaction)

        self.transactions = updated_transactions

    def combine_transaction(self):
        combined_transactions = []

        is_parsing_completed = False;

        for row in self.transactions:

            if True == is_parsing_completed:
                break

            row = row.values.tolist()

            for transaction in row:

                if True == is_parsing_completed:
                    break

                transaction = self.normalize_transaction(transaction)

                try:
                    transaction = self.error_handling( transaction )
                    transaction['category'] = self.categorize(transaction['particulars'])
                    combined_transactions.append( transaction )
                except Exception as error:

                    if self.STATEMENT_END == str( error ):
                        is_parsing_completed = True

                    if 'header' == str( error ):
                        continue

        self.transactions = combined_transactions

    def error_handling(self, transaction):

        if 'statement summary :' in transaction['particulars'].lower():
            raise Exception( self.STATEMENT_END );

        if 'date' in transaction['date'].lower():
            raise Exception( self.HEADER );

        if str == type( transaction['deposit'] ) and ' ' in transaction['deposit']:
            deposit, balance = transaction['deposit'].split(' ')
            transaction['deposit'] = deposit
            transaction['balance'] = balance

        transaction['withdrawal'] = self.maybe_convert_to_float( transaction['withdrawal'] )
        transaction['deposit'] = self.maybe_convert_to_float( transaction['deposit'] )
        transaction['balance'] = self.maybe_convert_to_float( transaction['balance'] )

        return transaction

    def normalize_transaction(self, transaction):

        bank = self.BANK_DETAILS[self.BANK]

        return {
            'date': transaction[ bank['date'] ] if self.index_exist(transaction, bank['date']) == True else numpy.nan,           # index of date column
            'particulars': transaction[ bank['particulars'] ] if self.index_exist(transaction, bank['particulars']) == True else numpy.nan,    # index of particulars column
            'chq': transaction[ bank['chq'] ] if self.index_exist(transaction, bank['chq']) == True else numpy.nan,            # index of cheque no. column
            'value_date': transaction[ bank['value_date'] ] if self.index_exist(transaction, bank['value_date']) == True else numpy.nan,      # index of value date column
            'withdrawal': transaction[ bank['withdrawal'] ] if self.index_exist(transaction, bank['withdrawal']) == True else numpy.nan,     # index of withdrawal column
            'deposit': transaction[ bank['deposit'] ] if self.index_exist(transaction, bank['deposit']) == True else numpy.nan,        # index of deposit column
            'balance': transaction[ bank['balance'] ] if self.index_exist(transaction, bank['balance']) == True else numpy.nan,        # index of balance column
        }

    def categorize(self, particular):
        # tokenizing
        word_list = list(tokenize(particular))

        # multiple similar statements
        if 'EMI' in word_list:
            return 'EMI'

        if 'UPI' in word_list:
            return 'UPI'

        if 'ATM' in word_list:
            return 'ATM'

        if 'NEFT' in word_list:
            return 'NEFT'

        if 'IMPS' in word_list:
            return 'IMPS'

        return numpy.nan

    def to_dataframe(self):
        self.transactions = pandas.DataFrame(self.transactions)

