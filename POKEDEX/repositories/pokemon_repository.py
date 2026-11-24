
class PokemonRepository:

    def __init__(self, conexao):
        self.conexao = conexao

    # CADASTRAR POKEMON
    def inserir(self, pokemon):

        cursor = self.conexao.cursor()

        sql = """
            INSERT INTO pokemon
            (numero, nome, tipo1, tipo2, altura, peso, descricao, imagem)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        valores = (
            pokemon.numero,
            pokemon.nome,
            pokemon.tipo1,
            pokemon.tipo2,
            pokemon.altura,
            pokemon.peso,
            pokemon.descricao,
            pokemon.imagem
        )

        try:
            cursor.execute(sql, valores)
            self.conexao.commit()

        except Exception:
            self.conexao.rollback()
            raise

        finally:
            cursor.close()


    # CONSULTAR POKEMON
    def consultar(self, pesquisa):

        cursor = self.conexao.cursor()

        try:
            if str(pesquisa).isdigit():

                sql = """
                    SELECT id, numero, nome, tipo1, tipo2,
                    altura, peso, descricao, imagem
                    FROM pokemon
                    WHERE numero = %s
                """

                cursor.execute(sql, (int(pesquisa),))

            else:

                sql = """
                    SELECT id, numero, nome, tipo1, tipo2,
                    altura, peso, descricao, imagem
                    FROM pokemon
                    WHERE nome LIKE %s
                """

                cursor.execute(sql, ("%" + pesquisa + "%",))

            resultado = cursor.fetchall()

            return resultado

        finally:
            cursor.close()


    # DELETAR POKEMON
    def deletar(self, numero):

        cursor = self.conexao.cursor()

        try:

            sql = "DELETE FROM pokemon WHERE numero = %s"

            cursor.execute(sql, (numero,))

            self.conexao.commit()

            return cursor.rowcount > 0

        except Exception:
            self.conexao.rollback()
            raise

        finally:
            cursor.close()
