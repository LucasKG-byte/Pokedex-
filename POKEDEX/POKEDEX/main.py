import tkinter as tk
from tkinter import messagebox
from Database.conexao import conectar
from API.pokeapi import trazer_imagem
from models.pokemon import Pokemon
from repositories.pokemon_repository import PokemonRepository

class PokemonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Pokédex")
        self.root.geometry("600x650")  
        self.root.config(bg="#f0f0f0")
        
        # Variável para manter a referência da imagem 
        self.img_poke = None

        # Esse troço faz a conexão
        self.conexao = conectar()
        if not self.conexao:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados!")
            self.root.destroy()
            return
        
        self.repo = PokemonRepository(self.conexao)

        self.criar_elementos()

    def criar_elementos(self):
        lbl_titulo = tk.Label(self.root, text="Gerenciador Pokedéx", font=("Arial", 16, "bold"), bg="#f0f0f0", fg="#333")
        lbl_titulo.pack(pady=10)
        
        frame_form = tk.LabelFrame(self.root, text=" Dados do Pokémon ", font=("Arial", 10, "bold"), bg="#f0f0f0", padx=10, pady=10)
        frame_form.pack(fill="x", padx=20, pady=5)
        
        self.campos = {}
        labels = ["Número:", "Nome:", "Tipo 1:", "Tipo 2:", "Altura:", "Peso:", "Descrição:"]
        for i, texto in enumerate(labels):
            lbl = tk.Label(frame_form, text=texto, bg="#f0f0f0", font=("Arial", 9, "bold"))
            lbl.grid(row=i, column=0, sticky="w", pady=4)

            if texto == "Descrição:":
                txt = tk.Text(frame_form, width=32, height=3, font=("Arial", 9))
                txt.grid(row=i, column=1, pady=4, sticky="w")
                self.campos["descricao"] = txt
            else:
                ent = tk.Entry(frame_form, width=35, font=("Arial", 9))
                ent.grid(row=i, column=1, pady=4, sticky="w")
                chave = texto.replace(":", "").lower().replace(" ", "")
                if chave == "número": chave = "numero"
                self.campos[chave] = ent

        # Botões
        frame_botoes = tk.Frame(self.root, bg="#f0f0f0")
        frame_botoes.pack(pady=10)

        btn_cadastrar = tk.Button(frame_botoes, text="Cadastrar", bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), width=9, command=self.cadastrar)
        btn_cadastrar.grid(row=0, column=0, padx=3)

        btn_consultar = tk.Button(frame_botoes, text="Consultar", bg="#2196F3", fg="white", font=("Arial", 9, "bold"), width=9, command=self.consultar)
        btn_consultar.grid(row=0, column=1, padx=3)

        btn_atualizar = tk.Button(frame_botoes, text="Atualizar", bg="#FF9800", fg="white", font=("Arial", 9, "bold"), width=9, command=self.atualizar)
        btn_atualizar.grid(row=0, column=2, padx=3)

        btn_deletar = tk.Button(frame_botoes, text="Deletar", bg="#F44336", fg="white", font=("Arial", 9, "bold"), width=9, command=self.deletar)
        btn_deletar.grid(row=0, column=3, padx=3)

        btn_limpar = tk.Button(frame_botoes, text="Limpar", bg="#9E9E9E", fg="white", font=("Arial", 9, "bold"), width=8, command=self.limpar)
        btn_limpar.grid(row=0, column=4, padx=3)

        frame_resultado = tk.LabelFrame(self.root, text=" Status / Resultado ", font=("Arial", 10, "bold"), bg="#f0f0f0", padx=10, pady=10)
        frame_resultado.pack(fill="both", expand=True, padx=20, pady=5)

        conteudo_res_frame = tk.Frame(frame_resultado, bg="#f0f0f0")
        conteudo_res_frame.pack(fill="both", expand=True)

        self.lbl_resultado = tk.Label(conteudo_res_frame, text="Pronto para uso.", bg="#f0f0f0", font=("Arial", 9), justify="left", anchor="nw")
        self.lbl_resultado.pack(side="left", fill="both", expand=True)

        self.lbl_imagem = tk.Label(conteudo_res_frame, bg="#f0f0f0")
        self.lbl_imagem.pack(side="right", padx=5, anchor="n")

    def limpar(self):
        for chave, widget in self.campos.items():
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            else:
                widget.delete(0, tk.END)
        self.lbl_resultado.config(text="Campos limpos.")
        self.lbl_imagem.config(image="")
        self.img_poke = None

    def cadastrar(self):
        try:
            numero = int(self.campos["numero"].get().strip())
            nome = self.campos["nome"].get().strip()
            tipo1 = self.campos["tipo1"].get().strip()
            tipo2 = self.campos["tipo2"].get().strip()
            altura = float(self.campos["altura"].get().strip())
            peso = float(self.campos["peso"].get().strip())
            descricao = self.campos["descricao"].get("1.0", tk.END).strip()

            if not nome:
                messagebox.showwarning("Aviso", "O nome do Pokémon é obrigatório!")
                return

            # Pega a função do pokeapi para baixar imagem[cite: 3]
            imagem = trazer_imagem(nome)

            pokemon = Pokemon(numero, nome, tipo1, tipo2, altura, peso, descricao, imagem)
            self.repo.inserir(pokemon)

            messagebox.showinfo("Deu certo", f"Pokémon {nome} cadastrado")
            self.limpar()
        except ValueError:
            messagebox.showerror("Verifique se Número, Altura e Peso foram preenchidos com números válidos.")
        except Exception as e:
            messagebox.showerror(f"Ocorreu um erro ao cadastrar: {e}")

    def consultar(self):
        try:
            pesquisa = (
                self.campos["nome"].get().strip()
                or self.campos["numero"].get().strip()
            )

            if not pesquisa:
                messagebox.showwarning(
                    "Aviso",
                    "Digite um Nome ou Número para consultar."
                )
                return

            resultados = self.repo.consultar(pesquisa)
            print("Resultados encontrados:", resultados)
            print("Quantidade:", len(resultados))

            if resultados:
                p = resultados[0]

                texto = (
                    f"Número: {p[1]}\n"
                    f"Nome: {p[2]}\n"
                    f"Tipo 1: {p[3]} | Tipo 2: {p[4] or 'Nenhum'}\n"
                    f"Altura: {p[5]}m | Peso: {p[6]}kg\n"
                    f"Descrição: {p[7]}"
                )

                self.lbl_resultado.config(text=texto)

                if p[8]:
                    try:
                        self.img_poke = tk.PhotoImage(data=p[8])
                        self.lbl_imagem.config(image=self.img_poke)
                    except Exception as e:
                        self.lbl_imagem.config(image="")
                        self.img_poke = None
                        print("Erro ao carregar imagem:", e)
                else:
                    self.lbl_imagem.config(image="")
                    self.img_poke = None

            else:
                messagebox.showinfo(
                    "Aviso",
                    "Pokémon não encontrado!"
                )

                self.lbl_resultado.config(text="Pokémon não encontrado.")
                self.lbl_imagem.config(image="")
                self.img_poke = None

        except Exception as e:
            messagebox.showerror(
                "Erro na consulta",
                f"Ocorreu um erro: {e}"
            )
    def atualizar(self):
        try:
            numero_str = self.campos["numero"].get().strip()

            if not numero_str.isdigit():
                messagebox.showwarning(
                    "Aviso",
                    "Informe o número do Pokémon para atualizar!"
                )
                return

            numero = int(numero_str)

            nome = self.campos["nome"].get().strip()
            tipo1 = self.campos["tipo1"].get().strip()
            tipo2 = self.campos["tipo2"].get().strip()
            altura = float(self.campos["altura"].get().strip())
            peso = float(self.campos["peso"].get().strip())
            descricao = self.campos["descricao"].get("1.0", tk.END).strip()

            if not nome:
                messagebox.showwarning(
                    "Aviso",
                    "O nome do Pokémon é obrigatório!"
                )
                return

            imagem = trazer_imagem(nome)

            pokemon = Pokemon(
                numero, nome, tipo1, tipo2,
                altura, peso, descricao, imagem
            )

            sucesso = self.repo.atualizar(numero, pokemon)

            if sucesso:
                messagebox.showinfo(
                    "Sucesso",
                    f"Pokémon {numero} atualizado!"
                )
                self.limpar()
            else:
                messagebox.showwarning(
                    "Aviso",
                    "Nenhum Pokémon encontrado com esse número."
                )

        except ValueError:
            messagebox.showerror(
                "Erro",
                "Verifique se Número, Altura e Peso possuem valores válidos."
            )

        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Ocorreu um erro ao atualizar: {e}"
            )    
    def deletar(self):
        numero_str = self.campos["numero"].get().strip()

        if not numero_str.isdigit():
            messagebox.showwarning(
                "Atenção",
                "Insira o número exato do Pokémon no campo 'Número:' para deletar."
            )
            return

        numero = int(numero_str)

        if messagebox.askyesno(
            "Confirmar exclusão",
         f"Tem certeza que deseja deletar o Pokémon {numero}?"
        ):
            try:
                self.repo.deletar(numero)

                messagebox.showinfo(
                    "Sucesso",
                    "Pokémon deletado com sucesso!"
                )

                self.limpar()

            except Exception as e:
                messagebox.showerror(
                    "Erro",
                    f"Ocorreu um erro ao deletar: {e}"
                )
    def __del__(self):
        if hasattr(self, 'conexao') and self.conexao and self.conexao.is_connected():
            self.conexao.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = PokemonApp(root)
    root.mainloop()