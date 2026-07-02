import tkinter as tk
from tkinter import messagebox, simpledialog
import os, json, csv, base64, subprocess, hashlib, calendar
from datetime import datetime

# --- CONFIGURAÇÕES ---
PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_DADOS = os.path.join(PASTA_ATUAL, "dados.bin")
ARQUIVO_HISTORICO = os.path.join(PASTA_ATUAL, "historico.bin")
ARQUIVO_LICENCA = os.path.join(PASTA_ATUAL, "licenca.txt")
SEGREDO_MESTRE = "FLUXUS_SISTEMA_PRIVADO_2024" 
MESES = ["JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", 
         "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]

# --- SEGURANÇA ---
def obter_id_pc():
    try:
        cmd = "wmic csproduct get uuid"
        res = subprocess.check_output(cmd, shell=True).decode().split('\n')
        return "".join(filter(str.strip, res[1:])).strip()
    except: return "PC-ID-ERRO"

def gerar_chave_final(id_pc):
    comb = (id_pc + SEGREDO_MESTRE).encode('utf-8')
    return hashlib.sha256(comb).hexdigest()[:8].upper()

def salvar_bin(d, cam):
    try:
        txt = json.dumps(d, indent=4).encode('utf-8')
        with open(cam, 'wb') as f: f.write(base64.b64encode(txt))
    except: pass

def carregar_bin(cam, default):
    if os.path.exists(cam):
        try:
            with open(cam, 'rb') as f:
                return json.loads(base64.b64decode(f.read()).decode('utf-8'))
        except: pass
    return default

class FluxusApp:
    def __init__(self, root):
        self.root = root
        self.pc_id = obter_id_pc()
        self.hoje = datetime.now()
        self.mes_nome = MESES[self.hoje.month - 1]
        
        self.d = carregar_bin(ARQUIVO_DADOS, {
            "reserva_total": 0.0, "divida_acumulada": 0.0, "receitas": {}, "gastos": {}, 
            "mes_ativo": self.hoje.month, "ano_ativo": self.hoje.year,
            "fixos_receitas": {}, "fixos_gastos": {}, "historico_mensal_do_ano": {}
        })
        self.h = carregar_bin(ARQUIVO_HISTORICO, {"anos": []})
        
        # Agora a função existe abaixo e não dará erro
        self.verificar_virada_tempo()
        
        self.root.title("Fluxus Digital")
        largura_app, altura_app = 400, 750
        self.root.geometry(f"{largura_app}x{altura_app}") # Simplificado para o exemplo
        self.root.configure(bg='#1E1E1E')
        self.root.resizable(False, False)

        self.montar_interface()
        self.atualizar_ui()
        
        # Trava de segurança agendada
        self.root.after(200, self.fluxo_seguranca)

    def fluxo_seguranca(self):
        if self.verificar_licenca():
            self.verificar_dia_pagamento()
        else:
            self.root.destroy()

    def verificar_licenca(self):
        correta = gerar_chave_final(self.pc_id)
        if os.path.exists(ARQUIVO_LICENCA):
            with open(ARQUIVO_LICENCA, 'r') as f:
                if f.read().strip().upper() == correta: return True
        while True:
            ch = simpledialog.askstring("Ativação", f"ID: {self.pc_id}\nChave:", parent=self.root)
            if ch is None: return False
            if ch.strip().upper() == correta:
                with open(ARQUIVO_LICENCA, 'w') as f: f.write(ch.strip().upper())
                return True
            messagebox.showerror("Erro", "Chave Inválida!", parent=self.root)

    def montar_interface(self):
        tk.Label(self.root, text="FLUXUS DIGITAL", fg="#A0A0A0", bg="#1E1E1E", font=("Arial", 14, "bold")).pack(pady=(20, 0))
        tk.Label(self.root, text=f"{self.mes_nome}", fg="#F8F8F2", bg="#1E1E1E", font=("Arial", 12, "italic")).pack(pady=(0, 10))
        self.lbl_total = tk.Label(self.root, text="DINHEIRO TOTAL: R$ 0.00", fg="#00FF00", bg="#1E1E1E", font=("Consolas", 12, "bold"))
        self.lbl_total.pack(pady=5)
        self.canvas_luz = tk.Canvas(self.root, width=60, height=60, bg='#1E1E1E', highlightthickness=0)
        self.canvas_luz.pack(pady=5)
        self.luz = self.canvas_luz.create_oval(10, 10, 50, 50, fill="#FF4400", outline="#FF4400")
        self.lbl_divida = tk.Label(self.root, text="BAGAGEM ANTIGA: R$ 0.00", bg="#1E1E1E", font=("Consolas", 10, "bold"))
        self.lbl_divida.pack(pady=10)
        self.lbl_receitas = tk.Label(self.root, text="SALDO (+): R$ 0.00", fg="#AFFC95", bg="#1E1E1E", font=("Arial", 10, "bold"))
        self.lbl_receitas.pack()
        self.lbl_gastos = tk.Label(self.root, text="ENCARGO (-): R$ 0.00", fg="#E6847A", bg="#1E1E1E", font=("Arial", 10, "bold"))
        self.lbl_gastos.pack(pady=5)
        self.frame_menu = tk.Frame(self.root, bg="#1E1E1E")
        self.frame_menu.pack(pady=20, fill="x")
        self.mostrar_menu_principal()

    def limpar_frame(self):
        for w in self.frame_menu.winfo_children(): w.destroy()

    def mostrar_menu_principal(self):
        self.limpar_frame()
        est = {"fg": "white", "relief": "flat", "font": ("Arial", 10, "bold"), "width": 25, "height": 2}
        tk.Button(self.frame_menu, text="GESTÃO FINANCEIRA", command=self.menu_fin, bg="#3498DB", **est).pack(pady=10)
        tk.Button(self.frame_menu, text="RELATÓRIOS", command=self.menu_rel, bg="#3498DB", **est).pack(pady=10)

    def menu_fin(self):
        self.limpar_frame()
        est = {"fg": "white", "relief": "flat", "font": ("Arial", 9, "bold"), "width": 25, "height": 2}
        tk.Button(self.frame_menu, text="NOVO LANÇAMENTO", command=self.lancar, bg="#2980B9", **est).pack(pady=5)
        tk.Button(self.frame_menu, text="GERENCIAR FIXOS", command=self.config_fixos, bg="#2980B9", **est).pack(pady=5)
        tk.Button(self.frame_menu, text="AMORTIZAR DÍVIDA", command=self.pagar_divida, bg="#E67E22", **est).pack(pady=5)
        tk.Button(self.frame_menu, text="<- VOLTAR", command=self.mostrar_menu_principal, bg="#7F8C8D", **est).pack(pady=15)

    def menu_rel(self):
        self.limpar_frame()
        est = {"fg": "white", "relief": "flat", "font": ("Arial", 9, "bold"), "width": 25, "height": 2}
        tk.Button(self.frame_menu, text="EXTRATO RÁPIDO", command=self.ver_extrato, bg="#2980B9", **est).pack(pady=5)
        tk.Button(self.frame_menu, text="BALANÇO ANUAL", command=self.ver_hist, bg="#2980B9", **est).pack(pady=5)
        tk.Button(self.frame_menu, text="EXPORTAR EXCEL", command=self.exportar_excel, bg="#27AE60", **est).pack(pady=5)
        tk.Button(self.frame_menu, text="<- VOLTAR", command=self.mostrar_menu_principal, bg="#7F8C8D", **est).pack(pady=15)

    def atualizar_ui(self):
        tr, tg = sum(self.d['receitas'].values()), sum(self.d['gastos'].values())
        self.lbl_total.config(text=f"TOTAL: R$ {self.d['reserva_total']:.2f}")
        div = self.d.get('divida_acumulada', 0)
        self.lbl_divida.config(text=f"BAGAGEM ANTIGA: R$ {div:.2f}", fg="#FF0000" if div > 0 else "#F8F8F2")
        self.lbl_receitas.config(text=f"SALDO (+): R$ {tr:.2f}"); self.lbl_gastos.config(text=f"ENCARGO (-): R$ {tg:.2f}")
        sobra = tr - tg
        cor = "#00FF00" if sobra > 100 else "#FFCC00" if sobra >= 0 else "#FF0000"
        self.canvas_luz.itemconfig(self.luz, fill=cor, outline=cor)

    def verificar_dia_pagamento(self):
        _, ult = calendar.monthrange(self.hoje.year, self.hoje.month)
        if self.hoje.day in [15, ult]:
            tg = sum(v for k,v in self.d['gastos'].items() if "[PAGO]" not in k)
            if tg > 0 and messagebox.askyesno("Liquidar", f"Pagar R$ {tg:.2f}?", parent=self.root):
                if self.d['reserva_total'] >= tg:
                    self.d['reserva_total'] -= tg
                    self.d['gastos'] = {f"[PAGO] {k}": 0.0 for k in self.d['gastos']}
                    salvar_bin(self.d, ARQUIVO_DADOS); self.atualizar_ui()

    def verificar_virada_tempo(self):
        ano, mes = self.hoje.year, self.hoje.month
        if self.d.get("ano_ativo", ano) < ano:
            self.h["anos"].append({"ano": self.d["ano_ativo"], "saldo": self.d["reserva_total"]})
            salvar_bin(self.h, ARQUIVO_HISTORICO); self.d.update({"ano_ativo": ano})
        if self.d.get("mes_ativo") != mes:
            sobra = sum(self.d['receitas'].values()) - sum(self.d['gastos'].values())
            if sobra < 0: self.d["divida_acumulada"] += abs(sobra)
            self.d.update({"receitas": self.d["fixos_receitas"].copy(), "gastos": self.d["fixos_gastos"].copy(), "mes_ativo": mes})
            salvar_bin(self.d, ARQUIVO_DADOS)

    def pagar_divida(self):
        v = simpledialog.askstring("Amortizar", "Valor para abater?", parent=self.root)
        if v:
            try:
                val = float(v.replace(',', '.'))
                self.d['reserva_total'] -= val; self.d['divida_acumulada'] -= val
                salvar_bin(self.d, ARQUIVO_DADOS); self.atualizar_ui()
            except: pass

    def ver_hist(self):
        jan = tk.Toplevel(self.root); jan.title("Anual"); jan.configure(bg="#1E1E1E")
        t = tk.Text(jan, bg="#2D2D2D", fg="white", font=("Consolas", 10)); t.pack(padx=10, pady=10)
        for r in self.h["anos"]: t.insert(tk.END, f"ANO {r['ano']}: R$ {r['saldo']:.2f}\n")
        t.config(state="disabled")

    def lancar(self):
        t = simpledialog.askstring("Tipo", "1: Saldo | 2: Gasto", parent=self.root)
        n = simpledialog.askstring("Item", "Nome:", parent=self.root)
        v = simpledialog.askstring("Valor", "R$:", parent=self.root)
        if t and n and v:
            try:
                val = float(v.replace(',', '.'))
                if t == "1": self.d["reserva_total"] += val; self.d["receitas"][n] = val
                else: self.d["gastos"][n] = val
                salvar_bin(self.d, ARQUIVO_DADOS); self.atualizar_ui()
            except: pass

    def config_fixos(self):
        t = simpledialog.askstring("Fixo", "1: Receita | 2: Gasto", parent=self.root)
        n = simpledialog.askstring("Nome", "Nome:", parent=self.root)
        v = simpledialog.askstring("Valor", "R$:", parent=self.root)
        if t and n and v:
            try:
                val = float(v.replace(',', '.'))
                c = "fixos_receitas" if t == "1" else "fixos_gastos"
                self.d[c][n] = val
                salvar_bin(self.d, ARQUIVO_DADOS); self.atualizar_ui()
            except: pass

    def ver_extrato(self):
        jan = tk.Toplevel(self.root); jan.title("Extrato"); jan.geometry("350x450"); jan.configure(bg="#1E1E1E")
        f = tk.Frame(jan, bg="#1E1E1E"); f.pack(expand=True, fill="both", padx=10, pady=10)
        lb = tk.Listbox(f, bg="#2D2D2D", fg="white", font=("Consolas", 10))
        lb.pack(side="left", expand=True, fill="both")
        mapa = []
        for k,v in self.d["receitas"].items(): lb.insert(tk.END, f"[+] {k}: {v:.2f}"); mapa.append(("receitas", k))
        for k,v in self.d["gastos"].items(): lb.insert(tk.END, f"[-] {k}: {v:.2f}"); mapa.append(("gastos", k))
        def apagar():
            if lb.curselection():
                tp, nm = mapa[lb.curselection()[0]]
                if tp == "receitas": self.d["reserva_total"] -= self.d[tp][nm]
                del self.d[tp][nm]; salvar_bin(self.d, ARQUIVO_DADOS); self.atualizar_ui(); jan.destroy()
        tk.Button(jan, text="APAGAR", command=apagar, bg="#E6847A", fg="white").pack(pady=10)

    def exportar_excel(self):
        nome = f"Fluxus_{self.hoje.month}.csv"
        try:
            with open(nome, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f, delimiter=';')
                w.writerow(['TIPO', 'ITEM', 'VALOR'])
                for k,v in self.d["receitas"].items(): w.writerow(['RECEITA', k, v])
                for k,v in self.d["gastos"].items(): w.writerow(['GASTO', k, v])
            messagebox.showinfo("Sucesso", f"Salvo como {nome}")
        except: pass

if __name__ == "__main__":
    app_root = tk.Tk()
    FluxusApp(app_root)
    app_root.mainloop()
