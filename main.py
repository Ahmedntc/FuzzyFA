import skfuzzy as fz
from skfuzzy import control as ctr
import numpy as np

class Fuzzy(object):
  def __init__(self):
    self.text = None
    self.point = 0
    self.posWords = ["bom","ótimo", "excelente", "incrível", "fantástico", "maravilhoso", "feliz", "surpreendente", "gosto", "bonito", "lindo", "deliciosa"]
    self.negWords = ["feio", "péssimo", "horrível", "terrível", "desagradável","frustrante", "decepcionante", "triste", "odeio", "lixo", "ruim", "desprezível"]
    self.intensifier  = ["muito", "bastante", "extremamente", "incrivelmente", "realmente", "completamente","demais"]
    self.neg  = ["não", "jamais", "nenhum", "nem", "nada", "nunca"]
    
    KeyPos= ctr.Antecedent(np.arange(0, 2, 1), "FP")
    KeyNeg = ctr.Antecedent(np.arange(0, 2, 1), "FN")
    KeyInten = ctr.Antecedent(np.arange(0, 2, 1), "I")
    KeyNegat = ctr.Antecedent(np.arange(0, 2, 1), "N")

    KeyPos.automf(number=2,  names=["Nao", "Sim"])
    KeyNeg.automf(number=2, names=["Nao", "Sim"])
    KeyInten.automf(number=2, names=["Nao", "Sim"])
    KeyNegat.automf(number=2, names=["Nao", "Sim"])
    
    feel = ctr.Consequent(np.arange(0, 11, 1), "Sentimento")
    
    feel["MNegativo"] = fz.trimf(feel.universe, [0, 0, 3])
    feel["Negativo"] =  fz.trimf(feel.universe, [1, 3, 5])
    feel["Neutro"] =    fz.trimf(feel.universe, [3, 5, 7])
    feel["Positivo"] =  fz.trimf(feel.universe, [5, 7, 9])
    feel["MPositivo"] = fz.trimf(feel.universe, [7, 10, 10])
    
    rul1 = ctr.Rule(KeyPos["Sim"], feel["Positivo"])
    rul2 = ctr.Rule(KeyPos["Sim"]  & KeyInten["Sim"], feel["MPositivo"])
    rul3 = ctr.Rule(KeyPos["Sim"]  & KeyNegat["Sim"], feel["Negativo"]) 
    rul4 = ctr.Rule(KeyNeg["Sim"], feel["Negativo"])
    rul5 = ctr.Rule(KeyNeg["Sim"] & KeyInten["Sim"], feel["MNegativo"])
    rul6 = ctr.Rule(KeyNeg["Sim"] & KeyNegat["Sim"], feel["Positivo"])
    rul7 = ctr.Rule(KeyNeg["Nao"] & KeyPos["Nao"], feel["Neutro"])
    
    Rules = ctr.ControlSystem([rul1, rul2, rul3, rul4, rul5, rul6, rul7])
    self.sys = ctr.ControlSystemSimulation(Rules)

  def SetText(self,text=str):
    self.text = text
    str = text.split(" ")
    #Todos os antecedentes devem ter valores de entrada!     
    self.sys.input["FP"] = 0  # Key word positiva
    self.sys.input["FN"] = 0  # key word negativa
    self.sys.input["I"] = 0   # Intensificador
    self.sys.input["N"] = 0   # Palavra de negação
    
    #output do split = lista de palavras em um texto
    
    # Olhamos a palavra anterior e posterior da nossa key word para ver se ha um intensificador ou um negação
    for i in range(0,len(str)):
      # Key word positiva
      if str[i] in self.posWords:
        self.sys.input["FP"] = 1
        #Se as palavras anteriores forem um intensificador ou negação
        if i >= 1:
          if str[i-1] in self.intensifier:
            self.sys.input["I"] = 1
            return
          elif str[i-1] in self.neg:
            self.sys.input["N"] = 1
            return
        #Se as palavras posteriores forem um intensificador ou negação
        if len(str[i+1:]) >= 1:
          if str[i+1] in self.intensifier:
            self.sys.input["I"] = 1
            return
          elif str[i+1] in self.neg:
            self.sys.input["N"] = 1
            return

      # key word negativa
      elif str[i] in self.negWords:
        self.sys.input["FN"] = 1
        #Se as palavras anteriores forem um intensificador ou negação
        if i >= 1:
          if str[i-1] in self.intensifier:
            
            self.sys.input["I"] = 1
            return
          elif str[i-1] in self.neg:
            self.sys.input["N"] = 1
            return

        #Se as palavras posteriores forem um intensificador ou negação
        if len(str[i+1:]) >= 1:
          if str[i+1] in self.intensifier:
            self.sys.input["I"] = 1
            return
          elif str[i+1] in self.neg:
            self.sys.input["N"] = 1
            return

  
  def Compute(self):
    self.sys.compute()
    self.point = self.sys.output["Sentimento"]
  def ShowRaw(self):
    print(self.point)
  def PolaridadeSentimento(self):
    if self.point > 0  and self.point < 3:
      print("Negativo")
    elif self.point > 2 and self.point < 6:
      print("Neutro")
    elif self.point > 4 and self.point < 10:
      print("Positivo")


if "__main__" == __name__:
    fuz = Fuzzy()
    phrases = ["Este gato é muito bonito","Este gato é lind", "Este gato é muito feio", "Não gostei deste filme", "Odiei essa série", "Amei muito essa música", "Esse música é um lixo", 
               "Esse filme é horrível", "Sua comida é deliciosa", "Esse cheiro é muito bom", "Esse cheiro é ruim",
               "Perder é frustrante demais"]
    for i in range(len(phrases)):
      fuz.SetText(phrases[i])
      fuz.Compute()
      print("Frase:\n" + phrases[i] + "\n")
      fuz.ShowRaw()
      print("\nResultado:")
      fuz.PolaridadeSentimento()
      print()
  
  