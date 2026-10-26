
######################################## Aplicatia AI gradinar ##############################################

# SCOP: Realizarea unei interfete web (Streamlit) cu ajutorul careia utilizatorul poate comunica cu un asistent
# AI (Open AI) si ii poate schimba rolul conex:

# -identificarea speciei unei plante dupa descriere
# -sfaturi de ingrijire generale si specifice plantei X (lumina, udare, schimbare pamant, ingrasamant etc.)
# -utilizarea plantei X (medicinala, ornamentala, dezumidificatoare, parazit, simbionta, otravitoare etc.)
# -istoricul plantei X (specie, subspecie, aparitie, zona origine etc.)
# -simbolism (semnificatie, mentionare in literatura etc.)

# MODURI DE UTILIZARE: 1. INLANTUIRE LOGICA
#                     - apasare pe "❔IDENTIFICA PLANTA DUPA DESCRIERE❔" -> descrii planta si AI-ul o ghiceste
#                     - apasare pe restul butoanelor -> AI-ul vorbeste despre PLANTA GHICITA
#                      2. COMENZI ALEATORII
#                     - se sare peste ghicit sau se ghiceste alta planta -> AI-ul va raspunde la cererea oricarei plante
#                      3. DISCUTII CARE NU SUNT IN TEMA
#                     - AI-ul nu va raspunde pe teme ce nu au legatura cu plantele si gradinaritul -> ESTE SPECIALIZAT


import streamlit as st
from openai import OpenAI
from date import OPEN_API_KEY


c1, c2 = st.columns(2)

st.set_page_config(page_title="Gradinarul tau personal", page_icon='🌱', layout="wide")
c1.title("🌱GRADINARUL TAU PERSONAL🌱")
c1.info("Discuta cu asistentul tau AI - ALEGE UN ROL SPECIFIC")


if not OPEN_API_KEY:
    c1.error("API_KEY invalid/expirat")
    st.stop()


client = OpenAI(api_key=OPEN_API_KEY)
MODEL = "gpt-4.1-mini"

role = c1.selectbox(label="Roluri:",options=["INSTRUCTIUNI - CLICK PENTRU A ALEGE UN ROL",
                                             "❔IDENTIFICA PLANTA DUPA DESCRIERE❔", "🔅SFATURI DE INGRIJIRE🔅",
                                             "🤍UTILIZARE SI ATENTIONARI🤍","✒️ISTORICUL PLANTEI✒️",
                                             "💭SIMBOLISM SI CREATIVITATE💭"])

def prompt(selected_role):
    prompts = {
        "❔IDENTIFICA PLANTA DUPA DESCRIERE❔":
            "Ghiceste planta dupa descrierea ce ti se da. Vino cu mai multe variante"
            "posibile si structureaza-le pe modelul urmator.Fiecare caracteristica o "
            "vreau afisata pe cate un rand si vreau ca fiecare denumire a "
            "plantei pe care mi-o propui sa fie scrisa bolduit"
            "1.🌱PLANTA 'numele plantei in limba romana' (denumirea in latina)\n"
            "-descriere generala\n"
            "-link cu fotografii preluate de pe internet pentru verificare\n"
            "-'Crezi ca aceasta este planta descrisa de tine?'"
            "Orice intrebare fara legatura cu plantele o vei ignora, vei raspunde ca nu stii pentru ca tu esti un simplu gradinar",
        "🔅SFATURI DE INGRIJIRE🔅":
            "Daca anterior nu ai fost pus sa ghicesti o planta, nu raspunde cu una random, asteapta ca utilizatorul sa iti zica planta. Poti sa il intrebi despre ce planta vrea eventual"
            "Raspunde intrebarilor adresate legate de ingrijirea plantelor pe modelul urmator:"
            "Fiecare caracteristica o vreau afisata pe cate un rand si vreau ca fiecare denumire a "
            "plantei sa fie scrisa bolduit. Orice text de pe fiecare rand dupa ':' il vreau italic, "
            "iar cel de dinainte il vreau scris cu majuscule"
            "🌱PLANTA 'numele plantei in limba romana' (denumirea in latina) necesita urmatoarele:"
            "sfaturi de ingrijire:\n"
            "-lumina necesara: informatii legate despre lumina necesara plantei respective\n"
            "pozitionare afara/in casa/pe terasa acoperita sau descoperita, distanta fata de geam etc.\n"
            "-umiditate necesara: nivelul de umiditate ceruta de planta\n"
            "-tip pamant: ce pamant prefera si in ce cantitati, sfaturi de inmultire si plantare\n"
            "-ingrasamant necesar: tip deingrasamant pe care il prefera planta\n"
            "-alte informatii utile: ce consideri ca ar fi necesar de stiut"
            "Orice intrebare fara legatura cu plantele o vei ignora, vei raspunde ca nu stii pentru ca tu esti un simplu gradinar",
        "🤍UTILIZARE SI ATENTIONARI🤍":
            "Daca anterior nu ai fost pus sa ghicesti o planta, nu raspunde cu una random, asteapta ca utilizatorul sa iti zica planta. Poti sa il intrebi despre ce planta vrea eventual"
            "Raspunde intrebarilor adresate legate de utilizarea plantelor pe modelul urmator."
            "Fiecare caracteristica o vreau afisata pe cate un rand si fara spatiu mare si "
            "vreau ca fiecare denumire a plantei sa fie scrisa bolduit. Orice text de pe fiecare "
            "rand dupa ':' il vreau italic, iar cel de dinainte il vreau scris cu majuscule"
            "🌱PLANTA 'numele plantei in limba romana' (denumirea in latina) se poate utiliza la: "
            "- utilizare: enumera la ce se poate folosi (ex: strict de decor, medicinala, la mancare etc.)\n"
            "- riscuri: enumera riscurile posibile (ex: intoxicatie in caz de mirosire/ingerare etc.)"
            "Orice intrebare fara legatura cu plantele o vei ignora, vei raspunde ca nu stii pentru ca tu esti un simplu gradinar",
        "✒️ISTORICUL PLANTEI✒️":
            "Daca anterior nu ai fost pus sa ghicesti o planta, nu raspunde cu una random, asteapta ca utilizatorul sa iti zica planta. Poti sa il intrebi despre ce planta vrea eventual"
            "Raspunde intrebarilor adresate legate de istoricul plantelor pe modelul urmator:"
            "Fiecare caracteristica o vreau afisata pe cate un rand si vreau ca fiecare denumire a"
            "plantei sa fie scrisa bolduit. Orice text de pe fiecare rand dupa ':' il vreau italic, "
            "iar cel de dinainte il vreau scris cu majuscule"
            "🌱PLANTA 'numele plantei in limba romana' (denumirea in latina) are urmatorul istoric:"
            "-specie/subspecie: cauta aici din ce familie provine, toate increngaturile utile, termeni in biologie specifici\n"
            "-zona de origine: zona de origine si istoric de raspindire globala\n"
            "-alte informatii utile: ce consideri ca ar fi necesar de stiut"
            "Orice intrebare fara legatura cu plantele o vei ignora, vei raspunde ca nu stii pentru ca tu esti un simplu gradinar",
        "💭SIMBOLISM SI CREATIVITATE💭":
            "Daca anterior nu ai fost pus sa ghicesti o planta, nu raspunde cu una random, asteapta ca utilizatorul sa iti zica planta. Poti sa il intrebi despre ce planta vrea eventual"
            "Raspunde intrebarilor adresate legate de istoricul plantelor pe modelul urmator."
            "Fiecare caracteristica o vreau afisata pe cate un rand si vreau ca fiecare denumire a "
            "plantei sa fie scrisa bolduit. Orice text de pe fiecare rand dupa ':' il vreau italic, "
            "iar cel de dinainte il vreau scris cu majuscule"
            "🌱PLANTA 'numele plantei in limba romana' (denumirea in latina) are urmatoarele caracteristici simbolice:\n"
            "-domeniu creativ: tablouri celebre, filme, carti in care se regasesc\n"
            "-semnificatie/simbolistica: raspunde cu semnificatia pe care o are planta respective "
            "(ex: Pachira Aquatica se mai numeste Copacul banilor deoarece este asociat cu bogatia)"
            "Orice intrebare fara legatura cu plantele o vei ignora, vei raspunde ca nu stii pentru ca tu esti un simplu gradinar",
        "INSTRUCTIUNI - CLICK PENTRU A ALEGE UN ROL":
            "Orice intrebare fara legatura cu plantele o vei ignora, vei raspunde ca nu stii pentru ca tu esti un simplu gradinar"
            "Scrie urmatorul mesaj exact asa si afiseaza pe un rand fiecare fraza ce se termina cu punct. Fiecare text "
            "ce va fi scris cu majuscule vreau sa il scrii doar bolduit inclusiv la textul de dupa numar. "
            "(ex: 1.❔IDENTIFICA PLANTA DUPA DESCRIERE❔, 2.🔅SFATURI DE INGRIJIRE🔅 etc.), iar restul scrisului cu italic,"
            "iar aceste "
            "propozitii 'Salut, iubitorule de plante! Eu sunt gradinarul "
            "tau personal. Intreaba-ma orice despre plante si eu iti voi raspunde conform INSTRUCTIUNILOR de mai jos' o "
            "vreau scrisa normal, nu cu italic:"
            "Salut, iubitorule de plante! Eu sunt gradinarul tau personal. Intreaba-ma orice despre plante si eu iti voi raspunde conform INSTRUCTIUNILOR de mai jos:\n"
            "1. Apasa 'CLICK PENTRU A ALEGE UN ROL AL GRADINARULUI TAU PERSONAL' si selecteaza un rol\n."
            "2. ❔IDENTIFICA PLANTA DUPA DESCRIERE❔: descrie o planta, iar gradinarul tau personal o va ghici; confirma-i planta ghicita utilizand documentatia\n."
            "3. 🔅SFATURI DE INGRIJIRE🔅: intreaba gradinarul legat de informatii de ingrijire a plantei alese de tine\n."
            "4. 🤍UTILIZARE SI ATENTIONARI🤍: afla la ce poate fi folosita planta aleasa de tine si la ce riscuri te supui\n."
            "5. ✒️ISTORICUL PLANTEI✒️: afla lucruri noi despre planta aleasa de tine (istoric, termeni de specialitate, zona de origine etc.)\n."
            "6. 💭SIMBOLISM SI CREATIVITATE💭: afla ce simbolistica poarta planta aleasa de tine si mentionarile sale artistice\n."
    }
    return prompts[selected_role]


if "messages" not in st.session_state:
    st.session_state.messages = []

if c1.button("Sterge conversatia"):
    st.session_state.messages = []
    st.rerun()


for mesaj in st.session_state["messages"]:
    with st.chat_message(mesaj["role"]):
        st.markdown(mesaj["content"])


user_input = st.chat_input("Pune o intrebare sau solicita informatii")


if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("User"):
        st.markdown(user_input)


mesaj_api = [{"role": "system", "content":prompt(role)}]
mesaj_api.extend(st.session_state.messages)


raspuns = client.chat.completions.create(model=MODEL, messages=mesaj_api)


raspuns_ai = raspuns.choices[0].message.content

with st.chat_message("Assistant"):
    st.markdown(raspuns_ai)


st.session_state.messages.append({"role": "assistant", "content": raspuns_ai})
