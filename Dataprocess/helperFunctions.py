
def translateNumToScenario(number: str):
    if  ( number == "1"):
        return "01 Norm-Norm"
    elif( number == "2"):
        return "02 TorN-TorN"
    elif( number == "3"):
        return "03 TorE-TorE"
    elif( number == "4"):
        return "04 TorS-TorS"
    elif( number == "5"):
        return "05 Loki-Loki"

    elif( number == "6"):
        return "06 Norm-TorN"
    elif( number == "7"):
        return "07 TorN-Norm"
    elif( number == "8"):
        return "08 Norm-TorE"
    elif( number == "9"):
        return "09 TorE-Norm"
    elif( number == "10"):
        return "10 Norm-TorS"
    elif( number == "11"):
        return "11 TorS-Norm"
    elif( number == "12"):
        return "12 Norm-Loki"
    elif( number == "13"):
        return "13 Loki-Norm"

    elif( number == "14"):
        return "14 TorN-TorE"
    elif( number == "15"):
        return "15 TorE-TorN"
    elif( number == "16"):
        return "16 TorN-TorS"
    elif( number == "17"):
        return "17 TorS-TorN"
    elif( number == "18"):
        return "18 TorE-TorS"
    elif( number == "19"):
        return "19 TorS-TorE"
    else:
        return "UNKNOWN!"

def getScenarioLabels( order) -> list[str]:
    labels = []
    for i in order:
        labels.append(translateNumToScenario(i))
    return labels
