
# from fuji_wrapper import fujiwrapper
# from foops_wrapper import foopswrapper
from someFAIR import somefFAIR



# fuji
# fuji = fujiwrapper.FujiWrapper()
# fuji_results = fuji.get_metric("https://doi.org/10.1186/2041-1480-4-37")
# print("F-UJI results:", fuji_results)

# foops
# foops = foopswrapper.FoopsWrapper()
# foops_results = foops.get_metric("https://w3id.org/okn/o/sd")
# print("Foops results:", foops_results)

# someFAIR
swFAIR = somefFAIR.SoftwareFAIRnessCalculator("https://github.com/dgarijo/Widoco/")
swFAIR.calculate_fairness()