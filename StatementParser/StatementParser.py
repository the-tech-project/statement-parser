###
# Bank statement parser.
###

from StatementParser.Banks import HDFC

import tabula


class StatementParser:

    def __init__(self, filename, bank):
        self.__output = self.__process(filename, bank)

    def __process(self, filename, bank):

        tabula_output = self.__read_statement(filename)

        if 'HDFC' == bank:
            return HDFC(tabula_output)

        return None

    def __read_statement(self, filename):

        # reading table using tabula
        return tabula.read_pdf(filename,
                               pages='all',
                               silent=True,
                               pandas_options={
                                   'header': None
                               })

    def get_transactions(self):
        return self.__output.transactions

    def get_debits(self):
        return self.__output.transactions.dropna(subset=['withdrawal'])

    def get_credits(self):
        return self.__output.transactions.dropna(subset=['deposit'])

    def get_opening_balance(self):
        transaction = self.__output.transactions.iloc[0]

        if transaction['deposit']:
            return transaction['balance'] - transaction['deposit']

        if transaction['withdrawal']:
            return transaction['balance'] + transaction['withdrawal']

        return None

    def get_closing_balance(self):
        return self.__output.transactions.iloc[-1]['balance']

    def to_list(self):
        return self.__output.transactions.to_dict('records')
