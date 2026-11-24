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
        self.root.geometry("550x580")
        self.root.config(bg="#f0f0f0")
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

        #Botões
        frame_botoes = tk.Frame(self.root, bg="#f0f0f0")
        frame_botoes.pack(pady=10)

        btn_cadastrar = tk.Button(frame_botoes, text="Cadastrar", bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), width=10, command=self.cadastrar)
        btn_cadastrar.grid(row=0, column=0, padx=5)

        btn_consultar = tk.Button(frame_botoes, text="Consultar", bg="#2196F3", fg="white", font=("Arial", 9, "bold"), width=10, command=self.consultar)
        btn_consultar.grid(row=0, column=1, padx=5)

        btn_deletar = tk.Button(frame_botoes, text="Deletar", bg="#F44336", fg="white", font=("Arial", 9, "bold"), width=10, command=self.deletar)
        btn_deletar.grid(row=0, column=2, padx=5)

        btn_limpar = tk.Button(frame_botoes, text="Limpar", bg="#9E9E9E", fg="white", font=("Arial", 9, "bold"), width=8, command=self.limpar)
        btn_limpar.grid(row=0, column=3, padx=5)

        frame_resultado = tk.LabelFrame(self.root, text=" Status / Resultado ", font=("Arial", 10, "bold"), bg="#f0f0f0", padx=10, pady=10)
        frame_resultado.pack(fill="both", expand=True, padx=20, pady=5)

        self.lbl_resultado = tk.Label(frame_resultado, text="Pronto para uso.", bg="#f0f0f0", font=("Arial", 9), justify="left", anchor="nw")
        self.lbl_resultado.pack(fill="both", expand=True)

    def limpar(self):
        for chave, widget in self.campos.items():
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            else:
                widget.delete(0, tk.END)
        self.lbl_resultado.config(text="Campos limpos.")

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

            #Pega a função do pokeapi para baixar imagem
            imagem = trazer_imagem(nome)

            pokemon = Pokemon(numero, nome, tipo1, tipo2, altura, peso, descricao, imagem)
            self.repo.inserir(pokemon)

            messagebox.showinfo("Deu certo", f"Pokémon {nome} cadastrado")
            self.limpar()
        except ValueError:
            messagebox.showerror("Erro", "Verifique se Número, Altura e Peso foram preenchidos com números válidos.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao cadastrar: {e}")

    def consultar(self):
        pesquisa = self.campos["nome"].get().strip() or self.campos["numero"].get().strip()
        if not pesquisa:
            messagebox.showwarning("Aviso", "Digite um Nome ou Número nos campos acima para consultar.")
            return

        resultados = self.repo.consultar(pesquisa)
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

            # Salva a imagem em disco como no seu código original do terminal
            if p[8]:
                nome_arquivo = f"pokemon_{p[1]}.png"
                with open(nome_arquivo, "wb") as arquivo:
                    arquivo.write(p[8])
                self.lbl_resultado.config(text=texto + f"\n\n[Imagem salva como: {nome_arquivo}]")
        else:
            messagebox.showinfo("Aviso", "Pokémon não encontrado!")
            self.lbl_resultado.config(text="Pokémon não encontrado.")

    def deletar(self):
        numero_str = self.campos["numero"].get().strip()
        if not numero_str.isdigit():
            messagebox.showwarning("Aviso", "Insira o número exato do Pokémon no campo 'Número:' para deletar.")
            return

        numero = int(numero_str)
        if messagebox.askyesno("Confirmação", f"Tem certeza que deseja deletar o Pokémon número {numero}?"):
            try:
                self.repo.deletar(numero)
                messagebox.showinfo("Sucesso", "Pokémon deletado com sucesso!")
                self.limpar()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao deletar: {e}")

    def __del__(self):
        if hasattr(self, 'conexao') and self.conexao and self.conexao.is_connected():
            self.conexao.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = PokemonApp(root)
    root.mainloop()