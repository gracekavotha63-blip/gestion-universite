# === INTRANET UCBC BENI - V10.4 COMPLET - PHOTO + CARTE D'ETUDIANT ===
import sqlite3, os, unicodedata, re, json
from datetime import datetime
from flask import Flask, request, redirect, render_template_string, send_file, send_from_directory, session, url_for

app = Flask(__name__)
app.secret_key = "ucbc-beni-2026-secret"
app.config['SESSION_PERMANENT'] = True

dossier = "intranet_beni"
UPLOAD_FOLDER = os.path.join(dossier, "fichiers")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
for _sub in ["photos","contenus","soumissions","messages","preuves"]:
    os.makedirs(os.path.join(UPLOAD_FOLDER, _sub), exist_ok=True)

ADMIN_USER = "admin"
ADMIN_PASS = "ucbc2026"

FACULTES = {
    "Sciences Economiques et de Gestion": ["Science de gestion","Informatique de Gestion", "Agri-Busness"],
    "Sciences de l'Information et de la Communication": ["Communication Appliquée"],
    "Theologie": ["Théologie Pastorale"],
    "Sciences de Philosophie, Éthique et Leadership": ["Leadership Éthique"],
    "Sciences Juridiques (Droit)": ["Droit (avec des orientations en Master en Droit Public et Droit Privé)"],
    "Technologie et Sciences de l'Ingénieur (Sciences Appliquées)": ["Génie Informatique","Génie Électromécanique"],
    "Sciences Psychologiques et de l'Éducation":["Sciences Psychologiques","Sciences de l'Éducation"]
}
NIVEAUX = ["L0", "L1", "L2", "L3", "M1", "M2"]
JOURS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
HEURES = ["8 to 9","9 to 10","10 to 11","11 to 12","12 to 1","1 to 2","2 to 3","3 to 4","4 to 5"]
GRADES = ["CT","PA","Ir","Msc","Ass","Dr"]
TRIMESTRES = ["Q1","Q2","Q3"]

# --- STYLE ---
STYLE = """
<style>
*{box-sizing:border-box}
body{margin:0;font-family:'Segoe UI',Arial,sans-serif;background:#F1F5F9;color:#0A1931}
a{text-decoration:none}
.wrap{max-width:1100px;margin:0 auto;padding:20px}
.box{background:#fff;border-radius:20px;padding:28px;box-shadow:0 10px 30px rgba(0,0,0,.08)}
h1{font-size:34px;line-height:1.2;margin:0}
h2{font-size:26px;margin:0 0 14px}
h3{font-size:19px;margin:20px 0 10px}
p{line-height:1.6}
.topbar{background:#0A1931;color:#fff;padding:14px 0;position:sticky;top:0;z-index:99}
.topbar-inner{max-width:1100px;margin:0 auto;padding:0 20px;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}
.logo-box{display:flex;align-items:center;gap:12px}
.logo-circle{width:52px;height:52px;background:#C9A227;color:#0A1931;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:22px;border:3px solid #fff;flex-shrink:0;overflow:hidden}
.logo-circle img{width:100%;height:100%;object-fit:cover}
.logo-text b{font-size:20px;letter-spacing:1px;display:block;line-height:1}
.logo-text span{font-size:12px;color:#C9A227;letter-spacing:1px}
.top-links{display:flex;gap:8px;flex-wrap:wrap}
.top-links a{color:#fff;background:rgba(255,255,255,.12);padding:9px 14px;border-radius:999px;font-size:14px;font-weight:600}
.top-links a:hover{background:#C9A227;color:#0A1931}
.hero{background:linear-gradient(135deg,#0A1931 0%,#0D3B8C 60%,#1A7A2E 100%);color:#fff;border-radius:22px;padding:36px 28px;margin:20px 0;display:flex;gap:24px;align-items:center;flex-wrap:wrap}
.hero-text{flex:1;min-width:280px}
.hero-text small{background:#C9A227;color:#0A1931;padding:6px 12px;border-radius:999px;font-weight:800;font-size:12px}
.hero-text h1{margin:14px 0 10px;font-size:38px}
.hero-text p{opacity:.9;font-size:16px;margin:0 0 20px}
.btn{display:inline-block;padding:13px 22px;border-radius:999px;font-weight:800;font-size:15px;border:none;cursor:pointer;text-align:center}
.btn-gold{background:#C9A227;color:#0A1931}
.btn-white{background:#fff;color:#0A1931}
.btn-green{background:#1A7A2E;color:#fff}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin-top:18px}
.card{display:block;padding:20px;border-radius:16px;color:#fff;font-weight:800;font-size:16px;line-height:1.4;box-shadow:0 6px 16px rgba(0,0,0,.1)}
.card small{font-weight:400;font-size:13px;opacity:.9;display:block;margin-top:6px}
.card-navy{background:#0A1931}.card-blue{background:#0D3B8C}.card-green{background:#1A7A2E}.card-gold{background:#C9A227;color:#0A1931}
.card:hover{transform:translateY(-3px);box-shadow:0 12px 24px rgba(0,0,0,.15)}
.info-card{display:flex;gap:16px;align-items:center;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:16px;padding:16px;margin-bottom:16px}
.avatar{width:78px;height:78px;border-radius:50%;object-fit:cover;border:3px solid #C9A227;flex-shrink:0;background:#ddd;display:flex;align-items:center;justify-content:center;font-size:28px}
.badge{display:inline-block;padding:5px 12px;border-radius:999px;font-size:12px;font-weight:800;background:#E0F2FE;color:#0D3B8C}
.badge-green{background:#DCFCE7;color:#166534}
label{font-weight:700;font-size:14px;display:block;margin:14px 0 6px}
input,select{width:100%;padding:12px 14px;border:1px solid #CBD5E1;border-radius:12px;font-size:15px;background:#fff}
button{padding:13px 20px;border-radius:12px;border:none;background:#0A1931;color:#fff;font-weight:800;cursor:pointer;width:100%;margin-top:16px}
table{width:100%;border-collapse:collapse;margin-top:12px;font-size:14px}
th{background:#0A1931;color:#fff;padding:12px;text-align:left}
td{padding:10px;border-bottom:1px solid #E2E8F0;vertical-align:middle}
.alert{padding:12px 16px;border-radius:12px;margin:12px 0;font-weight:600}
.alert-green{background:#DCFCE7;color:#166534}.alert-yellow{background:#FEF9C3;color:#854D0E}

/* --- NOUVEAU : BOUTONS DASHBOARD ENSEIGNANT --- */
.grille-enseignant{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:18px}
.grille-enseignant .card{min-height:110px;display:flex;flex-direction:column;justify-content:center}
@media(max-width:700px){.grille-enseignant{grid-template-columns:repeat(2,1fr)}}
@media(max-width:450px){.grille-enseignant{grid-template-columns:1fr}}
</style>
"""
JS_FAC = "<script>const FAC = " + json.dumps(FACULTES, ensure_ascii=False) + "; function updateDept(sel){ let f=document.getElementById('fac').value; let d=document.getElementById('dept'); if(!d) return; d.innerHTML=''; if(!FAC[f]){return;} FAC[f].forEach(function(x){ let o=document.createElement('option'); o.text=x; o.value=x; if(x==sel) o.selected=true; d.add(o); }); }</script>"

def header(titre=""):
    return '<div class="topbar"><div class="topbar-inner"><a href="/" style="color:#fff"><div class="logo-box"><div class="logo-circle" style="background:#fff;padding:3px;width:58px;height:58px"><img src="/logo_ucbc.png" style="width:100%;height:100%;object-fit:contain" onerror="this.style.display=\'none\';this.parentElement.innerHTML=\'UCBC\'"></div><div class="logo-text"><b>UCBC - BENI</b><span>UNIVERSITE CHRETIENNE BULINGUE DU CONGO</span></div></div></a><div class="top-links"><a href="/">Accueil</a><a href="/login">Espace Etudiant</a><a href="/enseignant/login">Espace Enseignant</a><a href="/admin/login">Admin</a></div></div></div>'
def back_top(url):
    return '<div style="padding:10px"><a href="'+url+'" style="text-decoration:none"><button style="width:auto;padding:8px 16px;background:#C9A227;color:#0A1931">Retour</button></a></div>'
def search_bar(q, ph):
    return '<form method="GET" style="display:flex;gap:8px"><input name="q" value="'+q+'" placeholder="'+ph+'" style="flex:1"><button style="width:auto;padding:12px 20px">Rechercher</button></form>'
def is_admin():
    return session.get('is_admin') == True
def match_q(q, *vals):
    if not q: return True
    q = q.lower()
    return any(q in str(v).lower() for v in vals if v is not None)
def pct(note):
    try: return round(float(note)/20*100,1)
    except: return 0
def same_promo(d1,n1,d2,n2):
    return d1==d2 and n1==n2
def cours_visible_pour(cours_id, dept, niv):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM cours WHERE id=?", (cours_id,)); c = cur.fetchone()
    if not c: conn.close(); return False
    if c['departement']==dept and c['niveau']==niv:
        conn.close(); return True
    cur.execute("SELECT * FROM cours_cibles WHERE cours_id=?", (cours_id,)); cibles = cur.fetchall(); conn.close()
    for x in cibles:
        if x['departement']==dept and x['niveau']==niv: return True
    return False
def generer_questions(texte, chap):
    phrases = [p.strip() for p in re.split(r'[.\n]', texte) if len(p.strip())>20]
    qs=[]
    for i in range(min(5, len(phrases) if phrases else 5)):
        base = phrases[i] if i < len(phrases) else "Notion importante du chapitre "+chap
        qs.append({"question":"Selon le cours "+chap+", que signifie : "+base[:90]+" ?","a":base[:60],"b":"Une notion secondaire","c":"Un exemple sans lien","d":"Aucune reponse","bonne":"A"})
    if not qs:
        for i in range(5): qs.append({"question":"Question "+str(i+1)+" - Chapitre "+chap+" ?","a":"Reponse A","b":"Reponse B","c":"Reponse C","d":"Reponse D","bonne":"A"})
    return qs
def get_db():
    db_path = os.path.join(dossier, "ucbc.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
def save_file(sub, f, prefix):
    if not f or f.filename=="": return ""
    ext = os.path.splitext(f.filename)[1] or ".jpg"
    nom = str(prefix).replace("/","_").replace(" ","_") + "_" + datetime.now().strftime("%Y%m%d%H%M%S") + ext
    dest = os.path.join(UPLOAD_FOLDER, sub)
    os.makedirs(dest, exist_ok=True)
    f.save(os.path.join(dest, nom))
    return nom
def next_mat():
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT COUNT(*) as nb FROM etudiants_propres"); n=cur.fetchone()['nb']; conn.close()
    return "UCBC/2026/%04d" % (n+1)
def next_paie():
    conn=get_db(); cur=conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) as nb FROM paiements"); n=cur.fetchone()['nb']
    except: n=0
    conn.close(); return "PAIE/2026/%04d" % (n+1)

# --- INIT DB ---
def init_db():
    conn=get_db(); cur=conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS etudiants_propres (matricule TEXT PRIMARY KEY, nom TEXT, gmail TEXT, faculte TEXT, departement TEXT, niveau TEXT, date_creation TEXT, photo TEXT, date_naissance TEXT, lieu_naissance TEXT, numero_carte TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS enseignants (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, gmail TEXT, mot_de_passe TEXT, grade TEXT, faculte TEXT, departement TEXT, niveau TEXT, date_creation TEXT, photo TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS cours (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, faculte TEXT, departement TEXT, niveau TEXT, prof TEXT, credits INTEGER, salle TEXT, trimestre TEXT, annee TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS cours_cibles (id INTEGER PRIMARY KEY AUTOINCREMENT, cours_id INTEGER, faculte TEXT, departement TEXT, niveau TEXT)")
        # --- MIGRATION CARTE UCBC ---
    for _t, _c in [("etudiants_propres","photo TEXT"),("etudiants_propres","date_naissance TEXT"),("etudiants_propres","lieu_naissance TEXT"),("etudiants_propres","numero_carte TEXT"),("enseignants","photo TEXT")]:
        try:
            _cols = [r[1] for r in cur.execute("PRAGMA table_info("+_t+")").fetchall()]
            _nom = _c.split()[0]
            if _nom not in _cols:
                cur.execute("ALTER TABLE "+_t+" ADD COLUMN "+_c)
        except:
            pass
    cur.execute("CREATE TABLE IF NOT EXISTS horaires (id INTEGER PRIMARY KEY AUTOINCREMENT, cours_id INTEGER, faculte TEXT, departement TEXT, niveau TEXT, jour TEXT, heure TEXT, trimestre TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS affectations (id INTEGER PRIMARY KEY AUTOINCREMENT, enseignant_id INTEGER, faculte TEXT, departement TEXT, niveau TEXT, cours_id INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS notes (matricule TEXT, cours_id INTEGER, note REAL, note_originale REAL, date_ajout TEXT, PRIMARY KEY(matricule,cours_id))")
    cur.execute("CREATE TABLE IF NOT EXISTS notes_travaux (id INTEGER PRIMARY KEY AUTOINCREMENT, matricule TEXT, cours_id INTEGER, type_travail TEXT, titre TEXT, note REAL, date_ajout TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS rattrapages (matricule TEXT, cours_id INTEGER, note_rattrapage REAL, date_ajout TEXT, PRIMARY KEY(matricule,cours_id))")
    cur.execute("CREATE TABLE IF NOT EXISTS contenus (id INTEGER PRIMARY KEY AUTOINCREMENT, enseignant_id INTEGER, cours_id INTEGER, titre TEXT, type TEXT, chapitre TEXT, description TEXT, fichier TEXT, date_envoi TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS soumissions (id INTEGER PRIMARY KEY AUTOINCREMENT, contenu_id INTEGER, matricule TEXT, fichier TEXT, commentaire TEXT, date_envoi TEXT, note REAL, feedback TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, expediteur_type TEXT, expediteur_id TEXT, expediteur_nom TEXT, destinataire_type TEXT, destinataire_id TEXT, cible_faculte TEXT, cible_departement TEXT, cible_niveau TEXT, sujet TEXT, message TEXT, fichier TEXT, date_envoi TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS recours (id INTEGER PRIMARY KEY AUTOINCREMENT, matricule TEXT, cours_id INTEGER, note_affichee REAL, note_reclamee REAL, motif TEXT, preuve_fichier TEXT, statut TEXT, reponse_jury TEXT, date_envoi TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY AUTOINCREMENT, enseignant_id INTEGER, cours_id INTEGER, chapitre TEXT, question TEXT, choix_a TEXT, choix_b TEXT, choix_c TEXT, choix_d TEXT, bonne_reponse TEXT, date_creation TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS paiements (id INTEGER PRIMARY KEY AUTOINCREMENT, numero_paie TEXT, matricule TEXT, montant_total REAL, montant_paye REAL, date_paiement TEXT, motif TEXT)")
    # --- NOUVEAU : TABLE APPEL / PRESENCE ENSEIGNANT ---
    cur.execute("CREATE TABLE IF NOT EXISTS presences (id INTEGER PRIMARY KEY AUTOINCREMENT, enseignant_id INTEGER, cours_id INTEGER, date_seance TEXT, matricule TEXT, statut TEXT, remarque TEXT, date_ajout TEXT)")
    # --- NOUVEAU : MIGRATION HORAIRE -> ENSEIGNANT + SALLE + HEURE DEBUT/FIN ---
    # C'est ici que ca se repercute : on ajoute enseignant_id a ta table horaires qui existe deja
    for _c in ["enseignant_id INTEGER", "salle TEXT", "heure_debut TEXT", "heure_fin TEXT"]:
        try:
            _cols = [r[1] for r in cur.execute("PRAGMA table_info(horaires)").fetchall()]
            _nom = _c.split()[0]
            if _nom not in _cols:
                cur.execute("ALTER TABLE horaires ADD COLUMN " + _c)
        except:
            pass
    conn.commit(); conn.close()
    # Migration si ancienne DB sans colonnes photo
    try:
        c=get_db(); cu=c.cursor()
        for col in ["photo TEXT","date_naissance TEXT","lieu_naissance TEXT","numero_carte TEXT"]:
            try: cu.execute("ALTER TABLE etudiants_propres ADD COLUMN "+col)
            except: pass
        try: cu.execute("ALTER TABLE enseignants ADD COLUMN photo TEXT")
        except: pass
        c.commit(); c.close()
    except: pass
init_db()

# --- ACCUEIL ---
@app.route('/')
def accueil():
    h = STYLE + header('accueil') + '<div class="wrap">'
    h += '<div class="hero"><div class="hero-text"><small>BIENVENUE A L\'UCBC BENI</small><h1>Being, transformed<br>to Transform</h1><p>Consulte ton horaire, tes notes, ta paie, tes cours et ta carte d\'etudiant, tout dans ton espace personnel.</p><a class="btn btn-gold" href="/login">Entrer dans mon Espace &rarr;</a> <a class="btn btn-white" href="/admin/login">Espace Admin</a></div><div style="background:#fff;color:#0A1931;border-radius:18px;padding:20px;min-width:240px;text-align:center"><div style="font-size:48px">🎓</div><b style="font-size:20px">UCBC - BENI</b><br><span style="color:#64748B">Amour • Travail • Fidelité</span><br><br><span class="badge">Annee 2026 - 2027</span> <span class="badge badge-green">Inscriptions Ouvertes</span></div></div>'
    h += '<div class="box"><h2 style="text-align:center">Que veux-tu faire ?</h2><div class="grille-enseignant">'
    h += '<a class="card card-navy" href="/login">👤 Mon Espace Etudiant<br><small>Voir ma carte, mes notes, mon horaire</small></a>'
    h += '<a class="card card-blue" href="/enseignant/login">👨‍🏫 Espace Enseignant<br><small>Cours, Notes, Presences</small></a>'
    h += '<a class="card card-green" href="/login">📊 Voir Mon Resultat<br><small>Notes, Jury, Rattrapage</small></a>'
    h += '<a class="card card-gold" href="/admin/login">⚙️ Administration<br><small>Pour le personnel UCBC</small></a>'
    h += '</div></div>'
    h += '<div class="box" style="margin-top:16px;text-align:center"><h3>Nos Facultes</h3><p>🔬 Technologie & Sciences de l\'Ingenieur &nbsp;•&nbsp; 💼 Sciences Economiques et de Gestion &nbsp;•&nbsp; 🌾 Sciences de l Information et de la Communication &nbsp;•&nbsp; ⚖️ Science Juridique (Droit) &nbsp;•&nbsp; 📖 Theologie</p></div></div>'
    return render_template_string(h)
@app.route('/logo_ucbc.png')
def logo_ucbc():
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    # On essaie tous les noms et tous les dossiers possibles
    noms = ["logo_ucbc.png", "logo.png", "UCBC.png", "logo_ucbc.jpg", "logo.jpg"]
    dossiers = [base, os.path.join(base, "static"), os.path.join(base, "uploads"), os.path.join(base, "images")]
    for dos in dossiers:
        for nom in noms:
            chemin = os.path.join(dos, nom)
            if os.path.exists(chemin):
                return send_file(chemin)
    return "Logo introuvable", 404
@app.route('/drapeau_rdc.png')
def drapeau_rdc():
    return send_file('drapeau_rdc.png', mimetype='image/png')

@app.route('/static/drapeau_rdc.png')
def drapeau_rdc_static():
    return send_file('drapeau_rdc.png', mimetype='image/png')

# --- LOGIN ETUDIANT + DASHBOARD ---
@app.route('/login-etudiant', methods=['GET','POST'])
def login_etudiant():
    msg=""
    if request.method=='POST':
        mat=request.form.get('matricule','').strip()
        conn=get_db(); cur=conn.cursor(); cur.execute("SELECT * FROM etudiants_propres WHERE matricule=?", (mat,)); e=cur.fetchone(); conn.close()
        if e: session['etudiant_mat']=mat; return redirect("/dashboard/"+mat)
        msg="Matricule introuvable. Demande a l Admin."
    alert='<div class="alert alert-red">'+msg+'</div>' if msg else ""
    return render_template_string(STYLE+header('etudiant')+back_top("/")+ '<div class="wrap"><div class="box" style="max-width:520px;margin:20px auto"><h2>Connexion Etudiant</h2>'+alert+'<form method="POST"><label>Matricule - ex: UCBC/2026/0001</label><input name="matricule" required placeholder="UCBC/2026/0001"><button>Se connecter</button></form></div></div>')
@app.route('/dashboard/<path:mat>')
def dashboard(mat):
    conn=get_db(); cur=conn.cursor(); cur.execute("SELECT * FROM etudiants_propres WHERE matricule=?", (mat,)); e=cur.fetchone()
    # --- JURY : on regarde le statut des cotes de cet etudiant ---
    try: cur.execute("ALTER TABLE notes ADD COLUMN statut TEXT DEFAULT 'brouillon'")
    except: pass
    try: cur.execute("ALTER TABLE notes ADD COLUMN phase TEXT DEFAULT 'normale'")
    except: pass
    # --- AUTO-FIX : colonne pour savoir si l'etudiant a deja vu le resultat ---
    try: cur.execute("ALTER TABLE etudiants_propres ADD COLUMN vu_jury TEXT DEFAULT ''")
    except: pass
    conn.commit()
    cur.execute("SELECT * FROM etudiants_propres WHERE matricule=?", (mat,)); e=cur.fetchone()
    cur.execute("SELECT statut, COUNT(*) as nb FROM notes WHERE matricule=? GROUP BY statut", (mat,)); stats = cur.fetchall()
    conn.close()
    if not e: return "Introuvable"
    photo = '<img class="avatar" src="/photo/etudiant/'+mat+'">' if (e['photo'] or "") else '<div class="avatar">👤</div>'
    # --- Message du Jury pour l'etudiant ---
    a_publie = [s for s in stats if s['statut'] and s['statut'].startswith('publie_')]
    a_soumis = [s for s in stats if s['statut'] in ('soumis_jury','valide_jury','brouillon')]
    if a_publie:
        # On prend la derniere phase publiee
        derniere_phase = a_publie[-1]['statut'].replace('publie_','').replace('_',' ').upper()
        # On regarde si l'etudiant a deja vu cette phase
        try: deja_vu = (e['vu_jury'] or "")
        except: deja_vu = ""
        if deja_vu == derniere_phase:
            # Deja vu -> on n'affiche plus le bandeau vert
            jury_msg = ''
        else:
            jury_msg = '<div style="background:#DCFCE7;border:2px solid #16A34A;border-radius:12px;padding:12px;margin-top:12px;text-align:center"><b style="color:#166534">✅ Resultats publies par le Jury : '+derniere_phase+'</b><br><small>Tu peux cliquer sur "Voir Mon Resultat".</small></div>'
    elif a_soumis:
        jury_msg = '<div style="background:#FFFBEB;border:2px solid #F59E0B;border-radius:12px;padding:12px;margin-top:12px;text-align:center"><b style="color:#92400E">⏳ En attente de deliberation du Jury</b><br><small>Tes cotes sont chez le Jury. Elles ne sont pas encore publiees. Reviens plus tard.</small></div>'
    else:
        jury_msg = '<div style="background:#F1F5F9;border:2px solid #CBD5E1;border-radius:12px;padding:12px;margin-top:12px;text-align:center"><b style="color:#475569">📭 Aucune cote pour le moment</b><br><small>Tes enseignants n\'ont pas encore remis les cotes au Jury.</small></div>'
    h = STYLE + header('etudiant') + back_top("/") + '<div class="wrap"><div class="box">'
    h += '<div class="info-card">'+photo+'<div style="flex:1"><h2 style="margin:0"> '+(e['nom'] or "")+' </h2><p style="margin:6px 0 0;color:#475569">Matricule : <b>'+mat+'</b> &nbsp;•&nbsp; '+(e['faculte'] or "")+'<br>'+(e['departement'] or "")+' - '+(e['niveau'] or "")+' &nbsp;•&nbsp; '+(e['gmail'] or "")+'</p><span class="badge">Etudiant UCBC</span> <span class="badge badge-green">Annee 2025-2026</span></div></div>'
    h += jury_msg
    h += '<div class="cards">'
    h += '<a class="card card-navy" href="/horaire/'+mat+'">🕐 Mon Horaire<br><small>Cours de la semaine</small></a>'
    h += '<a class="card card-blue" href="/notes/'+mat+'">📊 Voir Mon Resultat<br><small>Notes + Jury + Rattrapage</small></a>'
    h += '<a class="card card-green" href="/paie/'+mat+'">💰 Ma Paie<br><small>Frais & Paiements</small></a>'
    h += '<a class="card card-navy" href="/etudiant/contenus/'+mat+'">📚 Cours / TP / Quiz<br><small>Documents des profs</small></a>'
    h += '<a class="card card-navy" href="/messagerie-etudiant/'+mat+'">💬 Messagerie<br><small>Parler a l\'admin</small></a>'
    h += '<a class="card card-navy" style="background:#1A7A2E" href="/carte/'+mat+'">💳 Ma Carte d Etudiant<br><small>Voir + Imprimer</small></a>'
    h += '<a class="card card-navy" href="/recours/' + mat + '" style="grid-column:1/-1;background:#C9A227;color:#0A1931">✍️ Mes Recours<br><small>Faire un recours + Suivre mes demandes</small></a>'
    h += '</div></div></div>'
    return render_template_string(h)

@app.route('/recours/<path:mat>', methods=['GET','POST'])
@app.route('/etudiant/recours/<path:mat>', methods=['GET','POST'])
def etudiant_recours(mat):
    conn=get_db(); cur=conn.cursor(); cur.execute("SELECT * FROM etudiants_propres WHERE matricule=?", (mat,)); e=cur.fetchone()
    if not e: return "Introuvable"
    msg=""
    if request.method=='POST':
        fic=save_file("preuves", request.files.get('preuve'), mat.replace('/','_'))
        cur.execute("INSERT INTO recours (matricule,cours_id,note_affichee,note_reclamee,motif,preuve_fichier,statut,date_envoi) VALUES (?,?,?,?,?,?,?,?)", (mat, request.form.get('cours_id'), float(request.form.get('note_affichee') or 0), float(request.form.get('note_reclamee') or 0), request.form.get('motif'), fic, "En attente", datetime.now().strftime("%d/%m/%Y")))
        conn.commit(); msg="Recours envoye au Jury !"
    cur.execute("SELECT * FROM cours ORDER BY nom"); clist=cur.fetchall()
    cur.execute("SELECT recours.*, cours.nom as cours_nom FROM recours JOIN cours ON recours.cours_id=cours.id WHERE recours.matricule=? ORDER BY recours.id DESC", (mat,)); liste=cur.fetchall(); conn.close()
    opt="".join(["<option value='"+str(c['id'])+"'>"+c['nom']+" - "+c['departement']+" - "+c['niveau']+"</option>" for c in clist])
    lignes="".join(["<tr><td>"+r['cours_nom']+"</td><td>"+str(r['note_affichee'])+"</td><td>"+str(r['note_reclamee'])+"</td><td>"+r['motif']+"</td><td>"+r['statut']+" - "+(r['reponse_jury'] or "")+"</td></tr>" for r in liste]) or "<tr><td colspan='5' style='text-align:center'>Aucun recours.</td></tr>"
    h = STYLE+header('etudiant')+back_top("/dashboard/"+mat)+'<div class="wrap"><div class="box"><h2>Mes Recours - '+e['nom']+'</h2><p style="text-align:center;color:green"><b>'+msg+'</b></p><form method="POST" enctype="multipart/form-data"><select name="cours_id">'+opt+'</select><input name="note_affichee" type="number" step="0.5" placeholder="Note affichee /20" required><input name="note_reclamee" type="number" step="0.5" placeholder="Note reclamee /20" required><textarea name="motif" placeholder="Motif..." required></textarea><input type="file" name="preuve"><button class="green">Envoyer mon recours</button></form><table><tr><th>Cours</th><th>Affichee</th><th>Reclamee</th><th>Motif</th><th>Statut</th></tr>'+lignes+'</table></div></div>'
    return render_template_string(h)
# --- HORAIRE ETUDIANT ---
@app.route('/horaire/<path:mat>')
def horaire(mat):
    q = request.args.get('q','')
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM etudiants_propres WHERE matricule=?", (mat,)); e = cur.fetchone()
    if not e: return "Introuvable"
    cur.execute("SELECT horaires.*, cours.nom as nom, cours.prof as prof, cours.credits as credits, cours.salle as salle_cours FROM horaires JOIN cours ON horaires.cours_id=cours.id"); allh = cur.fetchall()
    rows = []
    for r in allh:
        if cours_visible_pour(r['cours_id'], e['departement'], e['niveau']) and match_q(q, r['nom'], r['prof']): rows.append(r)
    conn.close()
    grid = {}
    for j in JOURS:
        for hh in HEURES: grid[(j,hh)] = ""
    for r in rows: grid[(r['jour'], r['heure'])] = (r['nom'] or "") + "<br>(" + (r['prof'] or "") + "), " + str(r['credits'] or "") + " crdts<br><b>Salle: " + (r['salle_cours'] or "Non définie") + "</b>"
    def cell(jour, heure):
        v = grid.get((jour,heure),"")
        if v: return '<td class="horaire-cours">' + v + '</td>'
        if heure == "10 to 11" and jour in ("Monday","Friday"): return '<td class="horaire-chapel">Chapel</td>'
        if heure == "10 to 11" and jour in ("Wednesday"): return '<td class="horaire-expose">Exposé</td>'
        if heure == "1 to 2": return '<td class="horaire-pause">pause</td>'
        if heure == "2 to 3" and jour in ("Tuesday"): return '<td class="horaire-work">Work Program</td>'
        if jour == "Saturday": return '<td class="horaire-tp">TP</td>'
        return '<td style="background:#E5E7EB"></td>'
    lh = ""
    for hh in HEURES:
        lh += "<tr><td class='horaire-time'>"+hh+"</td>"
        for j in JOURS: lh += cell(j,hh)
        lh += "</tr>"
    css_horaire = "<style>table.horaire{width:100%;border-collapse:collapse;background:#fff;min-width:750px}.horaire-top{background:#0A1931;color:#fff;font-weight:900;font-size:22px;text-align:center;padding:14px;text-transform:uppercase}.horaire-sub{background:#C9A227;color:#0A1931;font-weight:800;font-size:15px;text-align:center;padding:8px}.horaire-day{background:#0A1931;color:#fff;font-weight:800;text-align:center;padding:12px;font-size:14px}.horaire-time{background:#0E8A4A;color:#fff;font-weight:800;text-align:center;padding:10px;font-size:13px;white-space:nowrap}.horaire-cours{background:#DBEAFE;color:#0A1931;text-align:center;padding:10px;font-size:12px;line-height:1.4;font-weight:600;border:1px solid #BFDBFE}.horaire-chapel{background:#FEF3C7;color:#92400E;text-align:center;padding:10px;font-size:12px;font-weight:800;border:1px solid #FDE68A}.horaire-expose{background:#E0E7FF;color:#3730A3;text-align:center;padding:10px;font-size:12px;font-weight:800;border:1px solid #C7D2FE}.horaire-pause{background:#FDE68A;color:#92400E;text-align:center;padding:10px;font-size:12px;font-weight:800}.horaire-work{background:#DCFCE7;color:#166534;text-align:center;padding:10px;font-size:12px;font-weight:800;border:1px solid #BBF7D0}.horaire-tp{background:#E9D5FF;color:#6B21A8;text-align:center;padding:10px;font-size:12px;font-weight:800;border:1px solid #DDD6FE}</style>"
    h = css_horaire + STYLE + header('etudiant') + back_top("/dashboard/"+mat) + '<div class="wrap"><div class="box" style="padding:0;overflow:hidden"><div style="padding:20px 20px 0">'+search_bar(q,"Rechercher un cours...")+'</div><div style="overflow-x:auto"><table class="horaire"><tr><td colspan="7" class="horaire-top">Faculte '+(e['faculte'] or "")+'</td></tr><tr><td colspan="7" class="horaire-sub">Horaire des cours Q1 ANNEE 2026-2027</td></tr><tr><td colspan="7" class="horaire-sub">'+(e['niveau'] or "")+' - '+(e['departement'] or "")+'</td></tr><tr><td style="background:#0E8A4A"></td><td class="horaire-day">Monday</td><td class="horaire-day">Tuesday</td><td class="horaire-day">Wednesday</td><td class="horaire-day">Thursday</td><td class="horaire-day">Friday</td><td class="horaire-day" style="background:#4A4A4A">Saturday</td></tr>'+lh+'</table></div></div></div>'
    return render_template_string(h)

# --- PAIE ETUDIANT + COORDONNEES BANCAIRES ---
@app.route('/paie/<path:mat>')
def paie(mat):
    q = request.args.get('q','')
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM etudiants_propres WHERE matricule=?", (mat,)); e = cur.fetchone()
    if not e: return "Introuvable"
    cur.execute("SELECT * FROM paiements WHERE matricule=? ORDER BY date_paiement ASC", (mat,)); allp = cur.fetchall(); conn.close()
    liste = [r for r in allp if match_q(q, r['motif'], r['date_paiement'], r['numero_paie'] or "")]
    total = allp[0]['montant_total'] if allp else 0
    paye = sum([r['montant_paye'] for r in allp]) if allp else 0
    reste = total - paye
    pourcent = int((paye/total*100)) if total>0 else 0
    cumul = 0; lignes = ""
    for r in liste:
        cumul += r['montant_paye']; solde = total - cumul
        coul = "#059669" if solde<=0 else "#DC2626"
        lignes += "<tr><td><b>"+(r['numero_paie'] or "-")+"</b></td><td>"+r['date_paiement']+"</td><td>"+r['motif']+"</td><td>"+str(r['montant_paye'])+" $</td><td>"+str(round(r['montant_paye']/total*100,1) if total else 0)+"%</td><td><b>"+str(cumul)+" $</b></td><td><b style='color:"+coul+"'>"+str(solde)+" $</b></td></tr>"
    if not liste: lignes = "<tr><td colspan='7' style='text-align:center'>Aucun paiement.</td></tr>"
    statut = "SOLDE - Tout paye" if total>0 and reste<=0 else "INCOMPLET" if total>0 else "En attente"
    logo = '<img src="/logo_ucbc.png" style="width:80px;height:80px;object-fit:contain">' if os.path.exists(os.path.join(dossier, "logo_ucbc.png")) else '<div style="width:80px;height:80px;border:2px dashed #0A1931;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:11px;text-align:center">LOGO<br>UCBC</div>'
    h = STYLE + header('etudiant') + back_top("/dashboard/"+mat) + '<div class="wrap"><div class="box"><div class="no-print" style="text-align:right"><button onclick="window.print()" style="width:auto;padding:10px 20px;background:#0A1931">Imprimer mon Releve</button></div>'
    coord = '<div style="background:#FFFBEB;border:2px solid #C9A227;border-radius:14px;padding:18px;margin:16px 0">'
    coord += '<h3 style="text-align:center;color:#991B1B;margin-top:0">COORDONNEES BANCAIRES DE L UCBC</h3>'
    coord += '<p style="text-align:center;font-size:13px">Conformement aux dispositions relatives a la bancarisation des paiements a l UCBC, tous les frais academiques et autres frais dus a l Universite doivent etre payes exclusivement par voie bancaire ou electronique, sauf dispositions derogatoires.</p>'
    coord += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:14px 0">'
    coord += '<div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:14px"><h4 style="color:#0D3B8C;margin:0">Compte 1 - EQUITY-BCDC, agence de Beni</h4><p>Intitule du compte : <b>UNIVERSITE CHRETIENNE BILINGUE DU CONGO</b><br>Devise : <b>USD</b><br>Numero de compte / IBAN : <b>00011150 666200182277154</b><br>SWIFT : <b>BCDCCDKIXXXX</b></p></div>'
    coord += '<div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:14px"><h4 style="color:#0D3B8C;margin:0">Compte 2 - RAWBANK, agence de Beni</h4><p>Intitule du compte : <b>CI-UCBC V/C USD</b><br>Devise : <b>USD</b><br>Numero de compte / IBAN : <b>05100-05171-01022331202-19</b><br>SWIFT : <b>RAWBCDKI</b></p></div>'
    coord += '</div>'
    coord += '<p style="text-align:center;font-size:13px">Les coordonnees de paiement par Mobile Money seront communiquees ulterieurement.</p>'
    coord += '<div style="background:#FEF2F2;border:1px solid #FCA5A5;border-radius:10px;padding:12px;text-align:center"><b>Note : Lors de tout paiement, les references suivantes doivent obligatoirement etre indiquees : Nom - Postnom et Prenom de l etudiant - Numero matricule.</b><br>Ton matricule : <b>' + mat + '</b> | Ton nom : <b>' + e['nom'] + '</b><br>Exemple de reference a ecrire a la banque : <b>' + e['nom'] + ' - ' + mat + '</b></div>'
    coord += '</div>'
    h += coord
    h += '<div style="text-align:center;border-bottom:3px solid #C9A227;padding-bottom:14px;display:flex;gap:16px;align-items:center;justify-content:center"><img src="/logo_ucbc.png" style="width:90px;height:90px;object-fit:contain;border-radius:50%;background:white;padding:5px"><div><h2 style="margin:0">UCBC - Beni</h2><p style="margin:0">Releve de Compte Etudiant</p><h3 style="margin:0">RELEVE DE COMPTE - ' + e['nom'] + '</h3></div></div>'
    h += '<p>Matricule : '+mat+'<br>Nom : '+e['nom']+'<br>Faculte : '+e['faculte']+' | Departement : '+e['departement']+' | Niveau : '+e['niveau']+'<br>Date : '+datetime.now().strftime("%d/%m/%Y %H:%M")+'</p>'
    h += '<div class="kpi"><div><b>'+str(total)+' $</b>Total</div><div><b>'+str(paye)+' $</b>Paye</div><div><b>'+str(reste)+' $</b>Reste<br>'+str(pourcent)+'% paye</div></div><div class="progress"><div class="bar" style="width:'+str(pourcent)+'% ">'+str(pourcent)+'%</div></div><p style="text-align:center"><b>'+statut+'</b></p>'
    h += '<div class="no-print">'+search_bar(q,"Rechercher... N Paie, motif...")+'</div><h3>Historique - Avec N Paie</h3><table><tr><th>N Paie</th><th>Date</th><th>Motif</th><th>Paye</th><th>%</th><th>Cumul</th><th>Solde</th></tr>'+lignes+'</table>'
    h += '<div style="margin-top:30px;display:flex;justify-content:space-between;border-top:1px solid #E5E7EB;padding-top:14px"><div>Signature Etudiant<br><br>__________________</div><div style="text-align:right">Signature Comptabilite<br><br>__________________<br>Cachet UCBC</div></div></div></div>'
    return render_template_string(h)

# --- CONTENUS ETUDIANT ---
@app.route('/etudiant/contenus/<path:mat>', methods=['GET','POST'])
def etudiant_contenus(mat):
    q = request.args.get('q','')
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM etudiants_propres WHERE matricule=?", (mat,)); e = cur.fetchone()
    if not e: return "Introuvable"
    msg = ""
    if request.method == 'POST':
        cid = request.form.get('contenu_id')
        fic = save_file("soumissions", request.files.get('fichier'), mat.replace('/','_'))
        cur.execute("INSERT INTO soumissions (contenu_id, matricule, fichier, commentaire, date_envoi) VALUES (?,?,?,?,?)", (cid, mat, fic, request.form.get('commentaire',''), datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit(); msg = "Ton TP a ete envoye a l'enseignant !"
    cur.execute("SELECT contenus.*, cours.nom as cours_nom, enseignants.nom as ens_nom, enseignants.grade as ens_grade FROM contenus JOIN cours ON contenus.cours_id=cours.id LEFT JOIN enseignants ON contenus.enseignant_id=enseignants.id"); allc = cur.fetchall()
    contenus = [c for c in allc if cours_visible_pour(c['cours_id'], e['departement'], e['niveau']) and match_q(q, c['titre'], c['cours_nom'], c['type'])]
    cur.execute("SELECT * FROM soumissions WHERE matricule=?", (mat,)); mes = {s['contenu_id']: s for s in cur.fetchall()}; conn.close()
    lignes = ""
    for c in contenus:
        s = mes.get(c['id'])
        if s: etat = "Rendu le " + s['date_envoi'] + "<br>Note : " + str(s['note'] if s['note'] is not None else "Pas encore corrige") + " / 20<br>" + (s['feedback'] or "")
        else: etat = "Pas encore rendu"
        lien = ""
        if c['fichier']: lien = '<a href="/fichier/contenus/'+c['fichier']+'" target="_blank">Telecharger le fichier</a>'
        form_r = ""
        if c['type'] in ('TP','Quiz','Devoir'):
            form_r = '<form method="POST" enctype="multipart/form-data" style="margin-top:8px"><input type="hidden" name="contenu_id" value="'+str(c['id'])+'"><input type="file" name="fichier" accept=".doc,.docx,.xls,.xlsx,.csv,.ppt,.pptx,.pdf,.jpg,.jpeg,.png" required><input name="commentaire" placeholder="Commentaire"><button class="green" style="padding:10px">Rendre mon TP</button></form>'
        lignes += "<tr><td><b>"+c['titre']+"</b><br>"+c['cours_nom']+" - Chapitre : "+c['chapitre']+"<br><span class='badge purple'>"+c['type']+"</span><br>Par "+(c['ens_grade'] or "")+" "+(c['ens_nom'] or "")+" - "+c['date_envoi']+"</td><td>"+c['description']+"<br>"+lien+"</td><td>"+etat+form_r+"</td></tr>"
    if not contenus: lignes = "<tr><td colspan='3' style='text-align:center'>Aucun cours / TP / Quiz pour le moment.</td></tr>"
    alert = '<div class="alert alert-green">'+msg+'</div>' if msg else ""
    h = STYLE + header('etudiant') + back_top("/dashboard/"+mat) + '<div class="wrap"><div class="box"><h2>Cours / TP / Quiz - ' + e['nom'] + '</h2><p>Telecharge le TP, fais-le, puis renvoie-le en Word, Excel, CSV, PowerPoint ou PDF.</p>'+alert+search_bar(q,"Rechercher...")+'<table><tr><th>Cours / TP / Quiz</th><th>Description + Fichier</th><th>Mon rendu + Note</th></tr>'+lignes+'</table></div></div>'
    return render_template_string(h)

# --- MESSAGERIE ETUDIANT ---
@app.route('/messagerie-etudiant/<path:mat>', methods=['GET','POST'])
def messagerie_etudiant(mat):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM etudiants_propres WHERE matricule=?", (mat,)); e = cur.fetchone()
    if not e: return "Introuvable"
    msg = ""
    if request.method == 'POST':
        eid = request.form.get('enseignant_id')
        fic = save_file("messages", request.files.get('fichier'), mat.replace('/','_'))
        cur.execute("INSERT INTO messages (expediteur_type, expediteur_id, expediteur_nom, destinataire_type, destinataire_id, sujet, message, fichier, date_envoi) VALUES ('etudiant', ?, ?, 'enseignant', ?, ?, ?, ?, ?)", (mat, e['nom'], eid, request.form.get('sujet',''), request.form.get('message',''), fic, datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit(); msg = "Message envoye a l'enseignant !"
    cur.execute("SELECT * FROM enseignants ORDER BY nom"); ens_list = cur.fetchall()
    cur.execute("SELECT * FROM messages WHERE (destinataire_type='etudiant' AND destinataire_id=?) OR (destinataire_type='promotion' AND cible_departement=? AND cible_niveau=?) OR destinataire_type='tous' OR (expediteur_type='etudiant' AND expediteur_id=?) ORDER BY id DESC", (mat, e['departement'], e['niveau'], mat)); msgs = cur.fetchall(); conn.close()
    opt = "".join(["<option value='"+str(r['id'])+"'>"+r['grade']+" "+r['nom']+" - "+r['departement']+" - "+r['niveau']+"</option>" for r in ens_list]) or "<option>Aucun enseignant</option>"
    lignes = ""
    for m in msgs:
        direction = "Moi -> " if m['expediteur_type']=='etudiant' and m['expediteur_id']==mat else "Enseignant -> Moi"
        lien = ""
        if m['fichier']: lien = '<a href="/fichier/messages/'+m['fichier']+'" target="_blank">Voir fichier</a>'
        lignes += "<tr><td><b>"+m['sujet']+"</b><br>"+m['date_envoi']+" - "+direction+" "+m['expediteur_nom']+"</td><td>"+m['message']+"<br>"+lien+"</td></tr>"
    if not msgs: lignes = "<tr><td colspan='2' style='text-align:center'>Aucun message.</td></tr>"
    alert = '<div class="alert alert-green">'+msg+'</div>' if msg else ""
    h = STYLE + header('etudiant') + back_top("/dashboard/"+mat) + '<div class="wrap"><div class="box"><h2>Messagerie - ' + e['nom'] + '</h2>'+alert+'<div style="background:#EFF6FF;border:2px solid #0D3B8C;border-radius:12px;padding:16px"><h3>Envoyer un message a un enseignant</h3><form method="POST" enctype="multipart/form-data"><select name="enseignant_id">'+opt+'</select><input name="sujet" placeholder="Sujet" required><textarea name="message" placeholder="Message..." required></textarea><input type="file" name="fichier"><button>Envoyer</button></form></div><h3>Mes messages</h3><table><tr><th>Sujet</th><th>Message</th></tr>'+lignes+'</table></div></div>'
    return render_template_string(h)

@app.route('/fichier/<sub>/<filename>')
def fichier_dl(sub, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, sub), filename)
# --- LOGIN + DASHBOARD ENSEIGNANT ---
@app.route('/enseignant/login', methods=['GET','POST'])
@app.route('/login-enseignant', methods=['GET','POST'])
def login_enseignant():
    msg = ""
    if request.method == 'POST':
        conn = get_db(); cur = conn.cursor()
        # --- MEME colonne que l'admin : gmail + mot_de_passe ---
        cur.execute("SELECT id FROM enseignants WHERE gmail=? AND mot_de_passe=?", (request.form.get('gmail','').strip().lower(), request.form.get('password','').strip()))
        u = cur.fetchone(); conn.close()
        if u:
            session['enseignant_id'] = u['id']
            return redirect("/dashboard-enseignant/" + str(u['id']))
        msg = "Gmail ou mot de passe incorrect. Demande a l'Admin de verifier ton nouveau mot de passe."
    alert = '<div class="alert alert-red">'+msg+'</div>' if msg else ""
    return render_template_string(STYLE + header('enseignant') + back_top("/") + '<div class="wrap"><div class="box" style="max-width:520px;margin:20px auto"><h2>Connexion Enseignant</h2>'+alert+'<form method="POST"><label>Gmail</label><input name="gmail" type="email" required><label>Mot de passe</label><input name="password" type="password" required><button>Se connecter</button></form><p style="text-align:center;font-size:13px">Demande a l Admin de te creer un compte avec ton Grade.</p></div></div>')
@app.route('/dashboard-enseignant/<int:eid>')
@app.route('/dashboard-enseignant/<int:eid>')
def dashboard_enseignant(eid):
    if session.get('enseignant_id') != eid and not is_admin(): return redirect("/login-enseignant")
    conn = get_db(); cur = conn.cursor()

    # --- AUTO-FIX : cree la colonne lu si elle n'existe pas ---
    try:
        cur.execute("ALTER TABLE messages ADD COLUMN lu INTEGER DEFAULT 0")
        conn.commit()
    except:
        pass

    cur.execute("SELECT * FROM enseignants WHERE id=?", (eid,)); ens = cur.fetchone()
    if not ens: return "Enseignant introuvable"
    cur.execute("SELECT * FROM affectations WHERE enseignant_id=?", (eid,)); affs = cur.fetchall()
    cur.execute("SELECT COUNT(*) as nb FROM contenus WHERE enseignant_id=?", (eid,)); nb_cont = cur.fetchone()
    cur.execute("SELECT COUNT(*) as nb FROM soumissions JOIN contenus ON soumissions.contenu_id=contenus.id WHERE contenus.enseignant_id=?", (eid,)); nb_soum = cur.fetchone()
    cur.execute("SELECT COUNT(*) as nb FROM messages WHERE destinataire_type='enseignant' AND destinataire_id=? AND (lu=0 OR lu IS NULL)", (str(eid),)); nb_msg = cur.fetchone()
    cur.execute("SELECT * FROM messages WHERE destinataire_type='enseignant' AND destinataire_id=? ORDER BY id DESC LIMIT 5", (str(eid),)); der = cur.fetchall()

    # L'enseignant vient de voir ses messages -> on les marque comme lus
    cur.execute("UPDATE messages SET lu=1 WHERE destinataire_type='enseignant' AND destinataire_id=?", (str(eid),))
    conn.commit()
    conn.close()

    aff_txt = "<br>".join([a['faculte']+" - "+a['departement']+" - "+a['niveau'] for a in affs]) or ens['faculte']+" - "+ens['departement']+" - "+ens['niveau']
    lm = "".join(["<tr><td><b>"+m['sujet']+"</b><br>"+m['expediteur_nom']+" - "+m['date_envoi']+"</td><td>"+m['message'][:120]+"</td></tr>" for m in der]) or "<tr><td colspan='2' style='text-align:center'>Aucun message.</td></tr>"
    h = STYLE + header('enseignant') + back_top("/") + '<div class="wrap"><div class="box"><h2>Bonjour ' + ens['grade'] + ' ' + ens['nom'] + '</h2><p>Gmail : ' + ens['gmail'] + '<br>Grade : ' + ens['grade'] + '<br>J enseigne en :<br>' + aff_txt + '</p>'
    h += '<div class="kpi"><div><b>' + str(nb_cont['nb']) + ' contenus</b></div><div><b>' + str(nb_soum['nb']) + ' TP recus</b></div><div><b>' + str(nb_msg['nb']) + ' messages</b></div></div><div class="grille-enseignant">'
    h += '<a class="card card-navy" href="/enseignant/contenus/' + str(eid) + '">Mes Cours / TP / Quiz</a>'
    h += '<a class="card card-navy" href="/enseignant/questions/' + str(eid) + '">Generateur Questions<br><small>5 questions par chapitre</small></a>'
    h += '<a class="card card-navy" href="/enseignant/notes/' + str(eid) + '">Deposer les Cotes<br><small>TP / Quiz / Examen - Jury</small></a>'
    h += '<a class="card card-navy" href="/enseignant/tableau/' + str(eid) + '">Tableau des Cotes<br><small>Grille TP | Quiz | Examen</small></a>'
    h += '<a class="card card-navy" href="/enseignant/soumissions/' + str(eid) + '">TP Recus</a>'
    h += '<a class="card card-navy" href="/enseignant/messagerie/' + str(eid) + '">Messagerie</a>'
    h += '<a class="card card-navy" href="/enseignant/horaire">Mon Horaire<br><small>Jour / Heure / Salle</small></a>'
    h += '<a class="card card-navy" href="/enseignant/messagerie-jury/' + str(eid) + '">Ecrire au Jury<br><small>Probleme de cotes / deliberation</small></a></div>'
    return render_template_string(h)

@app.route('/enseignant/contenus/<int:eid>', methods=['GET','POST'])
def enseignant_contenus(eid):
    if session.get('enseignant_id') != eid and not is_admin(): return redirect("/login-enseignant")
    q = request.args.get('q',''); msg = ""
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM enseignants WHERE id=?", (eid,)); ens = cur.fetchone()
    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            cur.execute("DELETE FROM contenus WHERE id=?", (request.form.get('id'),)); msg = "Contenu supprime"
        else:
            fic = save_file("contenus", request.files.get('fichier'), "ens"+str(eid))
            cur.execute("INSERT INTO contenus (enseignant_id, cours_id, titre, type, chapitre, description, fichier, date_envoi) VALUES (?,?,?,?,?,?,?,?)", (eid, request.form.get('cours_id'), request.form.get('titre'), request.form.get('type'), request.form.get('chapitre'), request.form.get('description'), fic, datetime.now().strftime("%d/%m/%Y")))
            msg = "Contenu envoye aux etudiants !"
        conn.commit()
    cur.execute("SELECT * FROM cours ORDER BY nom"); clist = cur.fetchall()
    cur.execute("SELECT contenus.*, cours.nom as cours_nom FROM contenus LEFT JOIN cours ON contenus.cours_id=cours.id WHERE contenus.enseignant_id=? ORDER BY contenus.id DESC", (eid,)); allc = cur.fetchall()
    liste = [r for r in allc if match_q(q, r['titre'], r['cours_nom'], r['type'])]
    conn.close()
    opt = "".join(["<option value='"+str(r['id'])+"'>"+r['nom']+" - "+r['departement']+" - "+r['niveau']+"</option>" for r in clist])
    lignes = ""
    for r in liste:
        lien = ""
        if r['fichier']: lien = '<a href="/fichier/contenus/' + r['fichier'] + '" target="_blank">Voir fichier</a>'
        lignes += "<tr><td><b>" + r['titre'] + "</b><br>" + (r['cours_nom'] or "") + " - Chapitre " + (r['chapitre'] or "") + "<br><span class='badge purple'>" + (r['type'] or "") + "</span></td><td>" + (r['description'] or "") + "<br>" + lien + "</td><td>" + (r['date_envoi'] or "") + "</td><td><form method='POST'><input type='hidden' name='action' value='delete'><input type='hidden' name='id' value='" + str(r['id']) + "'><button class='btn-mini del' style='width:auto'>Supprimer</button></form></td></tr>"
    if not liste: lignes = "<tr><td colspan='4' style='text-align:center'>Aucun contenu.</td></tr>"
    ok = '<div class="alert alert-green">'+msg+'</div>' if msg else ""
    h = STYLE + header('enseignant') + back_top("/enseignant/dashboard") + '<div class="wrap"><h2>Mes Contenus - ' + (ens['nom'] if ens else "") + '</h2>' + ok + '<div class="box"><h3>Envoyer un contenu aux etudiants</h3><form method="post" enctype="multipart/form-data" style="background:#F8FAFC;padding:18px;border-radius:14px"><label>Cours</label><select name="cours_id">' + opt + '</select><label>Titre</label><input name="titre" required><label>Type</label><select name="type"><option>Cours</option><option>TP</option><option>Quiz</option><option>Devoir</option><option>Examen</option></select><label>Chapitre</label><input name="chapitre" placeholder="Ex: Chapitre 1"><label>Description</label><input name="description"><label>Fichier</label><input type="file" name="fichier"><button class="green">Envoyer</button></form>' + search_bar(q, "Rechercher un contenu...") + '<table><tr><th>Titre / Cours</th><th>Description</th><th>Date</th><th>Action</th></tr>' + lignes + '</table></div></div>'
    return render_template_string(h)

@app.route('/enseignant/questions/<int:eid>', methods=['GET','POST'])
def enseignant_questions(eid):
    if session.get('enseignant_id') != eid and not is_admin(): return redirect("/login-enseignant")
    msg = ""
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM enseignants WHERE id=?", (eid,)); ens = cur.fetchone()
    if request.method == 'POST':
        if request.form.get('action') == 'generer':
            texte = request.form.get('texte_cours',''); chap = request.form.get('chapitre',''); cid = request.form.get('cours_id')
            qs = generer_questions(texte, chap)
            for qq in qs: cur.execute("INSERT INTO questions (enseignant_id, cours_id, chapitre, question, choix_a, choix_b, choix_c, choix_d, bonne_reponse, date_creation) VALUES (?,?,?,?,?,?,?,?,?,?)", (eid, cid, chap, qq['question'], qq['a'], qq['b'], qq['c'], qq['d'], qq['bonne'], datetime.now().strftime("%d/%m/%Y")))
            conn.commit(); msg = str(len(qs)) + " questions generees pour " + chap + " !"
        elif request.form.get('action') == 'corriger':
            cur.execute("UPDATE questions SET question=?, choix_a=?, choix_b=?, choix_c=?, choix_d=?, bonne_reponse=? WHERE id=?", (request.form.get('question'), request.form.get('choix_a'), request.form.get('choix_b'), request.form.get('choix_c'), request.form.get('choix_d'), request.form.get('bonne_reponse'), request.form.get('qid'))); conn.commit(); msg = "Question corrigee !"
        elif request.form.get('action') == 'delete':
            cur.execute("DELETE FROM questions WHERE id=?", (request.form.get('qid'),)); conn.commit(); msg = "Question supprimee"
    cur.execute("SELECT * FROM cours ORDER BY nom"); clist = cur.fetchall()
    cur.execute("SELECT questions.*, cours.nom as cours_nom FROM questions LEFT JOIN cours ON questions.cours_id=cours.id WHERE questions.enseignant_id=? ORDER BY questions.id DESC LIMIT 30", (eid,)); liste = cur.fetchall(); conn.close()
    opt = "".join(["<option value='"+str(r['id'])+"'>"+r['nom']+" - "+r['departement']+" - "+r['niveau']+"</option>" for r in clist])
    lq = ""
    for r in liste: lq += "<tr><td><b>" + (r['cours_nom'] or "") + " - " + r['chapitre'] + " (ID " + str(r['id']) + ")</b><br>" + r['question'] + "</td><td>A) " + r['choix_a'] + "<br>B) " + r['choix_b'] + "<br>C) " + r['choix_c'] + "<br>D) " + r['choix_d'] + "<br><b>Bonne reponse : " + r['bonne_reponse'] + "</b></td><td><form method='POST'><input type='hidden' name='action' value='delete'><input type='hidden' name='qid' value='" + str(r['id']) + "'><button class='btn-mini del' style='width:auto'>Supprimer</button></form></td></tr>"
    if not liste: lq = "<tr><td colspan='3' style='text-align:center'>Aucune question. Colle ton cours ci-dessous.</td></tr>"
    h = STYLE + header('enseignant') + back_top("/dashboard-enseignant/"+str(eid)) + '<div class="wrap"><div class="box"><h2>Generateur de Questions - ' + ens['grade'] + ' ' + ens['nom'] + '</h2><p style="text-align:center;color:green"><b>' + msg + '</b></p><div style="background:#F3E8FF;border:2px solid #7C3AED;border-radius:12px;padding:16px"><h3>Generer des questions</h3><form method="POST"><input type="hidden" name="action" value="generer"><select name="cours_id">' + opt + '</select><input name="chapitre" placeholder="Chapitre ex: Chapitre 3" required><textarea name="texte_cours" placeholder="Colle ici le texte de ton cours..." style="min-height:140px" required></textarea><button class="purple">Generer au moins 5 questions</button></form></div><h3>Questions generees</h3><table><tr><th>Question</th><th>Choix + Bonne reponse</th><th>Action</th></tr>' + lq + '</table><h3>Corriger une question</h3><form method="POST"><input type="hidden" name="action" value="corriger"><input name="qid" type="number" placeholder="ID de la question a corriger" required><textarea name="question" placeholder="Question corrigee" required></textarea><input name="choix_a" placeholder="Choix A" required><input name="choix_b" placeholder="Choix B" required><input name="choix_c" placeholder="Choix C" required><input name="choix_d" placeholder="Choix D" required><select name="bonne_reponse"><option>A</option><option>B</option><option>C</option><option>D</option></select><button class="green">Corriger cette question</button></form></div></div>'
    return render_template_string(h)
@app.route('/enseignant/notes/<int:eid>', methods=['GET','POST'])
def enseignant_notes(eid):
    if session.get('enseignant_id') != eid and not is_admin(): return redirect("/login-enseignant")
    msg = ""
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM enseignants WHERE id=?", (eid,)); ens = cur.fetchone()
    if request.method == 'POST':
        cid = request.form.get('cours_id'); typ = request.form.get('type_travail'); titre = request.form.get('titre')
        mats = request.form.getlist("matricule_list"); vals = request.form.getlist("note_val")
        for m, n in zip(mats, vals):
            if n.strip() != "":
                cur.execute("INSERT INTO notes_travaux (matricule, cours_id, type_travail, titre, note, date_ajout) VALUES (?,?,?,?,?,?)", (m, cid, typ, titre, float(n), datetime.now().strftime("%d/%m/%Y")))
                if typ == 'Examen':
                    cur.execute("SELECT note_originale FROM notes WHERE matricule=? AND cours_id=?", (m, cid)); ex = cur.fetchone()
                    orig = ex['note_originale'] if ex and ex['note_originale'] is not None else float(n)
                    cur.execute("INSERT INTO notes (matricule, cours_id, note, note_originale, date_ajout) VALUES (?,?,?,?,?) ON CONFLICT(matricule, cours_id) DO UPDATE SET note=excluded.note, note_originale=COALESCE(notes.note_originale, excluded.note_originale)", (m, cid, float(n), orig, datetime.now().strftime("%d/%m/%Y")))
        conn.commit(); msg = "Cotes " + typ + " deposees ! Si Examen, elles vont au Jury."
    cur.execute("SELECT * FROM cours ORDER BY nom"); clist = cur.fetchall()
    sel = request.args.get('cours_id') or (str(clist[0]['id']) if clist else "")
    csel = None; etus = []
    if sel:
        cur.execute("SELECT * FROM cours WHERE id=?", (sel,)); csel = cur.fetchone()
        if csel:
            cur.execute("SELECT * FROM etudiants_propres"); alle = cur.fetchall()
            etus = sorted([e for e in alle if cours_visible_pour(int(sel), e['departement'], e['niveau'])], key=lambda x: x['matricule'])
    conn.close()
    opt = "".join(["<option value='"+str(r['id'])+"' "+("selected" if str(r['id'])==str(sel) else "")+">"+r['nom']+" - "+r['departement']+" - "+r['niveau']+"</option>" for r in clist])
    lignes = "".join(["<tr><td><b>"+e['matricule']+"</b><br>"+e['nom']+"</td><td><input type='hidden' name='matricule_list' value='"+e['matricule']+"'><input type='number' step='0.5' min='0' max='20' name='note_val' placeholder='Note /20'></td></tr>" for e in etus]) or "<tr><td colspan='2' style='text-align:center'>Aucun etudiant.</td></tr>"
    info = "<h3>"+csel['nom']+" - "+csel['departement']+" - "+csel['niveau']+"</h3>" if csel else ""
    h = STYLE + header('enseignant') + back_top("/dashboard-enseignant/"+str(eid)) + '<div class="wrap"><div class="box"><h2>Deposer les Cotes - ' + ens['grade'] + ' ' + ens['nom'] + '</h2><form method="GET"><select name="cours_id" onchange="this.form.submit()">' + opt + '</select></form>' + info + '<form method="post" enctype="multipart/form-data"><input type="hidden" name="cours_id" value="' + str(sel) + '"><select name="type_travail"><option>TP</option><option>Quiz</option><option>Examen</option></select><input name="titre" placeholder="Titre ex: TP 2, Quiz Chapitre 3, Examen Q1" required><table><tr><th>Etudiant</th><th>Note /20</th></tr>' + lignes + '</table><button class="green" style="margin-top:14px">Deposer les cotes vers Jury</button></form><p style="text-align:center;color:green"><b>' + msg + '</b></p></div></div>'
    return render_template_string(h)
    h = STYLE + ...  # ton ancien h deja la

    # --- DASHBOARD ENSEIGNANT - BOUTONS RANGES ---
    h += '''
    <style>
    .grid-ens{...}
    ...
    </style>
    <div class="grid-ens">
    ...
    </div>
    '''
    return render_template_string(h)
@app.route('/enseignant/tableau/<int:eid>')
def enseignant_tableau(eid):
    if session.get('enseignant_id') != eid and not is_admin(): return redirect("/login-enseignant")
    q = request.args.get('q','')
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM enseignants WHERE id=?", (eid,)); ens = cur.fetchone()
    cur.execute("SELECT * FROM cours ORDER BY nom"); clist = cur.fetchall()
    sel = request.args.get('cours_id') or (str(clist[0]['id']) if clist else "")
    csel = None; etus = []
    if sel:
        cur.execute("SELECT * FROM cours WHERE id=?", (sel,)); csel = cur.fetchone()
        if csel:
            cur.execute("SELECT * FROM etudiants_propres"); alle = cur.fetchall()
            etus = sorted([e for e in alle if cours_visible_pour(int(sel), e['departement'], e['niveau']) and match_q(q, e['nom'], e['matricule'])], key=lambda x: x['matricule'])
    lignes = ""
    for e in etus:
        cur.execute("SELECT AVG(note) as moy FROM notes_travaux WHERE matricule=? AND cours_id=? AND type_travail='TP'", (e['matricule'], sel)); tp = cur.fetchone()['moy']
        cur.execute("SELECT AVG(note) as moy FROM notes_travaux WHERE matricule=? AND cours_id=? AND type_travail='Quiz'", (e['matricule'], sel)); quiz = cur.fetchone()['moy']
        cur.execute("SELECT note FROM notes WHERE matricule=? AND cours_id=?", (e['matricule'], sel)); ex = cur.fetchone(); exam = ex['note'] if ex else None
        vals = [v for v in [tp, quiz, exam] if v is not None]
        moy = round(sum(vals)/len(vals),2) if vals else "-"
        moy_txt = str(moy) + " / 20 = " + str(pct(moy)) + "%" if moy != "-" else "-"
        lignes += "<tr><td><b>" + e['matricule'] + "</b><br>" + e['nom'] + "</td><td>" + (str(round(tp,2)) if tp else "-") + " / 20</td><td>" + (str(round(quiz,2)) if quiz else "-") + " / 20</td><td>" + (str(exam) if exam is not None else "-") + " / 20</td><td><b>" + moy_txt + "</b></td></tr>"
    conn.close()
    opt = "".join(["<option value='"+str(r['id'])+"' "+("selected" if str(r['id'])==str(sel) else "")+">"+r['nom']+" - "+r['departement']+" - "+r['niveau']+"</option>" for r in clist])
    h = STYLE + header('enseignant') + back_top("/dashboard-enseignant/"+str(eid)) + '<div class="wrap"><div class="box"><h2>Tableau des Cotes - Grille TP | Quiz | Examen - ' + ens['grade'] + ' ' + ens['nom'] + '</h2><form method="GET"><select name="cours_id" onchange="this.form.submit()">' + opt + '</select></form>' + search_bar(q, "Rechercher un etudiant...") + '<table><tr><th>Etudiant</th><th>Grille TP</th><th>Grille Quiz</th><th>Grille Examen</th><th>Moyenne</th></tr>' + (lignes or "<tr><td colspan='5' style='text-align:center'>Aucun etudiant.</td></tr>") + '</table></div></div>'
    return render_template_string(h)
@app.route('/enseignant/soumissions/<int:eid>', methods=['GET','POST'])
def enseignant_soumissions(eid):
    if session.get('enseignant_id') != eid and not is_admin(): return redirect("/login-enseignant")
    msg = ""
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM enseignants WHERE id=?", (eid,)); ens = cur.fetchone()
    if request.method == 'POST':
        cur.execute("UPDATE soumissions SET note=?, feedback=? WHERE id=?", (float(request.form.get('note')) if request.form.get('note') else None, request.form.get('feedback'), request.form.get('id'))); conn.commit(); msg = "TP corrige ! L'etudiant verra sa note."
    cur.execute("SELECT soumissions.*, contenus.titre as contenu_titre, contenus.type as contenu_type, etudiants_propres.nom as etu_nom FROM soumissions JOIN contenus ON soumissions.contenu_id=contenus.id JOIN etudiants_propres ON soumissions.matricule=etudiants_propres.matricule WHERE contenus.enseignant_id=? ORDER BY soumissions.id DESC", (eid,)); liste = cur.fetchall(); conn.close()
    lignes = ""
    for s in liste:
        lien = ""
        if s['fichier']: lien = '<a href="/fichier/soumissions/' + s['fichier'] + '" target="_blank">Telecharger le TP (Word / Excel / PPT)</a>'
        lignes += "<tr><td><b>" + s['etu_nom'] + "</b><br>" + s['matricule'] + "<br>" + s['date_envoi'] + "</td><td><b>" + s['contenu_titre'] + "</b> (" + s['contenu_type'] + ")<br>" + lien + "<br>" + (s['commentaire'] or "") + "</td><td><form method='POST'><input type='hidden' name='id' value='" + str(s['id']) + "'><input type='number' step='0.5' min='0' max='20' name='note' value='" + (str(s['note']) if s['note'] is not None else "") + "' placeholder='Note /20'><input name='feedback' placeholder='Feedback' value='" + (s['feedback'] or "") + "'><button class='green' style='padding:10px'>Corriger</button></form></td></tr>"
    if not liste: lignes = "<tr><td colspan='3' style='text-align:center'>Aucun TP recu.</td></tr>"
    h = STYLE + header('enseignant') + back_top("/dashboard-enseignant/"+str(eid)) + '<div class="wrap"><div class="box"><h2>TP Recus a Corriger - ' + ens['grade'] + ' ' + ens['nom'] + '</h2><p style="text-align:center;color:green"><b>' + msg + '</b></p><table><tr><th>Etudiant</th><th>TP Rendu</th><th>Correction</th></tr>' + lignes + '</table></div></div>'
    return render_template_string(h)
@app.route('/enseignant/messagerie/<int:eid>', methods=['GET','POST'])
def enseignant_messagerie(eid):
    if session.get('enseignant_id') != eid and not is_admin(): return redirect("/login-enseignant")
    msg = ""
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM enseignants WHERE id=?", (eid,)); ens = cur.fetchone()
    if request.method == 'POST':
        cible = request.form.get('cible')
        fic = save_file("messages", request.files.get('fichier'), "ens"+str(eid))
        if cible == 'tous':
            cur.execute("INSERT INTO messages (expediteur_type, expediteur_id, expediteur_nom, destinataire_type, destinataire_id, sujet, message, fichier, date_envoi) VALUES ('enseignant', ?, ?, 'tous', 'tous', ?, ?, ?, ?)", (str(eid), ens['nom'], request.form.get('sujet'), request.form.get('message'), fic, datetime.now().strftime("%d/%m/%Y %H:%M")))
        elif cible == 'promotion':
            cur.execute("INSERT INTO messages (expediteur_type, expediteur_id, expediteur_nom, destinataire_type, destinataire_id, cible_faculte, cible_departement, cible_niveau, sujet, message, fichier, date_envoi) VALUES ('enseignant', ?, ?, 'promotion', '', ?, ?, ?, ?, ?, ?, ?)", (str(eid), ens['nom'], request.form.get('cible_faculte'), request.form.get('cible_departement'), request.form.get('cible_niveau'), request.form.get('sujet'), request.form.get('message'), fic, datetime.now().strftime("%d/%m/%Y %H:%M")))
        else:
            cur.execute("INSERT INTO messages (expediteur_type, expediteur_id, expediteur_nom, destinataire_type, destinataire_id, sujet, message, fichier, date_envoi) VALUES ('enseignant', ?, ?, 'etudiant', ?, ?, ?, ?, ?)", (str(eid), ens['nom'], request.form.get('destinataire_id'), request.form.get('sujet'), request.form.get('message'), fic, datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit(); msg = "Message envoye !"
    cur.execute("SELECT * FROM etudiants_propres ORDER BY nom"); etus = cur.fetchall()
    cur.execute("SELECT * FROM messages WHERE (destinataire_type='enseignant' AND destinataire_id=?) OR (expediteur_type='enseignant' AND expediteur_id=?) ORDER BY id DESC", (str(eid), str(eid))); msgs = cur.fetchall(); conn.close()
    opt_etus = "".join(["<option value='"+r['matricule']+"'>"+r['nom']+" - "+r['matricule']+" - "+r['departement']+" - "+r['niveau']+"</option>" for r in etus])
    lignes = ""
    for m in msgs:
        direction = "Moi -> " if m['expediteur_type']=='enseignant' else "Etudiant -> Moi"
        cible_txt = "Tous" if m['destinataire_type']=='tous' else "Promotion " + (m['cible_departement'] or "") + " - " + (m['cible_niveau'] or "") if m['destinataire_type']=='promotion' else m['destinataire_id']
        lien = ""
        if m['fichier']: lien = '<a href="/fichier/messages/' + m['fichier'] + '" target="_blank">Voir fichier</a>'
        lignes += "<tr><td><b>"+m['sujet']+"</b><br>"+m['date_envoi']+" - "+direction+" "+m['expediteur_nom']+" -> "+cible_txt+"</td><td>"+m['message']+"<br>"+lien+"</td></tr>"
    if not msgs: lignes = "<tr><td colspan='2' style='text-align:center'>Aucun message.</td></tr>"
    fac_opt = "".join(["<option>"+f+"</option>" for f in FACULTES]); niv_opt = "".join(["<option>"+n+"</option>" for n in NIVEAUX])
    h = STYLE + header('enseignant') + back_top("/dashboard-enseignant/"+str(eid)) + '<div class="wrap"><div class="box"><h2>Messagerie - ' + ens['grade'] + ' ' + ens['nom'] + '</h2><p>Choisis ou envoyer : Une promotion, Tous, ou Un seul etudiant.</p><p style="text-align:center;color:green"><b>' + msg + '</b></p><div style="background:#EFF6FF;border:2px solid #0D3B8C;border-radius:12px;padding:16px"><h3>Envoyer un message</h3><form method="POST" enctype="multipart/form-data"><select name="cible" id="cible" onchange="document.getElementById(\'promo_fields\').style.display=this.value==\'promotion\'?\'block\':\'none\';document.getElementById(\'etu_field\').style.display=this.value==\'individuel\'?\'block\':\'none\'"><option value="promotion">Une Promotion</option><option value="tous">Tous les etudiants ou j enseigne</option><option value="individuel">Un seul etudiant</option></select><div id="promo_fields"><select name="cible_faculte" id="fac" onchange="updateDept(\'\')">' + fac_opt + '</select><select name="cible_departement" id="dept"></select><select name="cible_niveau">' + niv_opt + '</select></div><div id="etu_field" style="display:none"><select name="destinataire_id">' + opt_etus + '</select></div><input name="sujet" placeholder="Sujet" required><textarea name="message" placeholder="Message..." required></textarea><input type="file" name="fichier"><button>Envoyer le message</button></form></div><h3>Messages</h3><table><tr><th>Sujet</th><th>Message</th></tr>' + lignes + '</table></div></div><script>' + JS_FAC.replace("<script>","").replace("</script>","") + ' updateDept("");</script>'
    return render_template_string(h)
# ============================================================
# --- NOUVEAU : MESSAGERIE ENSEIGNANT <-> JURY ---
# ============================================================
@app.route('/enseignant/messagerie-jury/<int:eid>', methods=['GET','POST'])
def enseignant_messagerie_jury(eid):
    if session.get('enseignant_id') != eid and not is_admin(): return redirect("/login-enseignant")
    msg = ""
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM enseignants WHERE id=?", (eid,)); ens = cur.fetchone()
    if request.method == 'POST':
        # Enseignant ecrit au Jury
        cur.execute("INSERT INTO messages (expediteur_type, expediteur_id, expediteur_nom, destinataire_type, destinataire_id, sujet, message, date_envoi) VALUES ('enseignant', ?, ?, 'jury', 'jury', ?, ?, ?)",
                    (str(eid), ens['nom'], request.form.get('sujet'), request.form.get('message'), datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit(); msg = "Message envoye au Jury !"
    # On affiche les 2 sens : Enseignant -> Jury et Jury -> Enseignant
    cur.execute("SELECT * FROM messages WHERE (destinataire_type='jury' AND expediteur_id=?) OR (destinataire_type='enseignant' AND destinataire_id=? AND expediteur_type='jury') ORDER BY id DESC", (str(eid), str(eid)))
    msgs = cur.fetchall(); conn.close()
    lignes = ""
    for m in msgs:
        direction = "Moi -> Jury" if m['expediteur_type']=='enseignant' else "Jury -> Moi"
        lignes += "<tr><td><b>"+m['sujet']+"</b><br>"+m['date_envoi']+" - "+direction+"</td><td>"+m['message']+"</td></tr>"
    if not msgs: lignes = "<tr><td colspan='2' style='text-align:center'>Aucun message avec le Jury.</td></tr>"
    h = STYLE + header('enseignant') + back_top("/dashboard-enseignant/"+str(eid)) + '<div class="wrap"><div class="box"><h2>Ecrire au Jury - ' + ens['grade'] + ' ' + ens['nom'] + '</h2><p>En cas de difficulte sur les cotes, la deliberation, ou une erreur, ecrit ici au Jury.</p><p style="text-align:center;color:green"><b>' + msg + '</b></p><div style="background:#FFF7ED;border:2px solid #F59E0B;border-radius:12px;padding:16px"><h3>Nouveau message au Jury</h3><form method="POST"><input name="sujet" placeholder="Sujet ex: Erreur de cote TP 2 - L1 Info" required><textarea name="message" placeholder="Explique ton probleme..." required></textarea><button>Ecrire au Jury</button></form></div><h3>Conversation avec le Jury</h3><table><tr><th>Sujet</th><th>Message</th></tr>' + lignes + '</table></div></div>'
    return render_template_string(h)

@app.route('/jury/messagerie', methods=['GET','POST'])
def jury_messagerie():
    # Jury = Admin / Jury connecte. On utilise is_admin() comme pour le reste de ton code.
    if not is_admin(): return redirect("/login-admin")
    msg = ""
    conn = get_db(); cur = conn.cursor()
    if request.method == 'POST':
        # Jury repond a un enseignant precis
        cur.execute("INSERT INTO messages (expediteur_type, expediteur_id, expediteur_nom, destinataire_type, destinataire_id, sujet, message, date_envoi) VALUES ('jury', 'jury', 'Jury', 'enseignant', ?, ?, ?, ?)",
                    (request.form.get('destinataire_id'), request.form.get('sujet'), request.form.get('message'), datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit(); msg = "Reponse envoyee a l'enseignant !"
    cur.execute("SELECT * FROM enseignants ORDER BY nom"); elist = cur.fetchall()
    cur.execute("SELECT * FROM messages WHERE destinataire_type='jury' OR expediteur_type='jury' ORDER BY id DESC"); msgs = cur.fetchall(); conn.close()
    opt_ens = "".join(["<option value='"+str(r['id'])+"'>"+r['grade']+" "+r['nom']+"</option>" for r in elist])
    lignes = ""
    for m in msgs:
        direction = "Enseignant -> Jury" if m['expediteur_type']=='enseignant' else "Jury -> Enseignant " + m['destinataire_id']
        lignes += "<tr><td><b>"+m['sujet']+"</b><br>"+m['date_envoi']+" - "+direction+" - "+m['expediteur_nom']+"</td><td>"+m['message']+"</td></tr>"
    if not msgs: lignes = "<tr><td colspan='2' style='text-align:center'>Aucun message.</td></tr>"
    h = STYLE + header('admin') + back_top("/dashboard-admin") + '<div class="wrap"><div class="box"><h2>Messagerie Jury - Enseignants</h2><p style="text-align:center;color:green"><b>'+msg+'</b></p><div style="background:#EFF6FF;border:2px solid #0D3B8C;border-radius:12px;padding:16px"><h3>Repondre a un enseignant</h3><form method="POST"><select name="destinataire_id">'+opt_ens+'</select><input name="sujet" placeholder="Sujet" required><textarea name="message" placeholder="Reponse du Jury..." required></textarea><button>Envoyer a l\'enseignant</button></form></div><h3>Messages</h3><table><tr><th>Sujet</th><th>Message</th></tr>'+lignes+'</table></div></div>'
    return render_template_string(h)
# --- ADMIN ---
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    msg = ""
    if request.method == 'POST':
        if request.form.get('user') == ADMIN_USER and request.form.get('password') == ADMIN_PASS:
            session.permanent = True; session['is_admin'] = True; return redirect("/admin")
        msg = "Identifiant ou mot de passe incorrect."
    alert = '<div class="alert alert-red">'+msg+'</div>' if msg else ""
    return render_template_string(STYLE + header('admin') + back_top("/") + '<div class="wrap"><div class="box" style="max-width:460px;margin:20px auto"><h2>Espace Administration</h2>'+alert+'<form method="POST"><label>Identifiant</label><input name="user" required><label>Mot de passe</label><input name="password" type="password" required><button class="gold">Se connecter</button></form></div></div>')
@app.route('/admin/logout')
def admin_logout():
    session.clear(); return redirect("/admin/login")
@app.route('/admin', methods=['GET','POST'])
@app.route('/admin', methods=['GET','POST'])
@app.route('/dashboard-admin', methods=['GET','POST'])
def admin():
    if not is_admin(): return redirect("/admin/login")
    q = request.args.get('q',''); message = ""; edit = None
    conn = get_db(); cur = conn.cursor()
    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            cur.execute("DELETE FROM etudiants_propres WHERE matricule=?", (request.form.get('matricule'),)); message = "Etudiant supprime"
        else:
            mat = request.form.get('matricule','').strip() or next_mat()
            # --- PHOTO CORRIGEE : on enregistre toujours dans uploads ---
            photo_nom = ""
            fph = request.files.get('photo')
            if fph and fph.filename != "":
                import os
                base = os.path.dirname(os.path.abspath(__file__))
                dos_upload = os.path.join(base, "uploads")
                os.makedirs(dos_upload, exist_ok=True)
                ext = os.path.splitext(fph.filename)[1].lower() or ".jpg"
                if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
                    ext = ".jpg"
                photo_nom = mat.replace('/','_') + ext
                fph.save(os.path.join(dos_upload, photo_nom))
            # Si on modifie sans nouvelle photo, on garde l'ancienne
            if request.form.get('matricule'):
                cur.execute("SELECT photo FROM etudiants_propres WHERE matricule=?", (mat,)); _old = cur.fetchone()
                if not photo_nom and _old: photo_nom = _old[0] or ""
            # --- CORRECTION 12 COLONNES : on lit les vraies colonnes ---
            cur.execute("PRAGMA table_info(etudiants_propres)")
            cols_admin = [r[1] for r in cur.fetchall()]
            vals_admin = {
                'matricule': mat,
                'nom': request.form.get('nom','').strip(),
                'gmail': request.form.get('gmail','').strip().lower(),
                'faculte': request.form.get('faculte'),
                'departement': request.form.get('departement'),
                'niveau': request.form.get('niveau'),
                'date_inscription': datetime.now().strftime("%d/%m/%Y"),
                'date': datetime.now().strftime("%d/%m/%Y"),
                'photo': photo_nom,
                'date_naissance': request.form.get('date_naissance',''),
                'lieu_naissance': request.form.get('lieu_naissance',''),
                'numero_carte': request.form.get('numero_carte','') or mat[-4:],
                'telephone': request.form.get('telephone','') if request.form.get('telephone') else "",
                'mot_de_passe': "1234",
                'password': "1234",
                'mdp': "1234",
                'statut': "Actif",
            }
            cols_ok_admin = [c for c in cols_admin if c in vals_admin]
            vals_ok_admin = [vals_admin[c] for c in cols_ok_admin]
            cur.execute("INSERT OR REPLACE INTO etudiants_propres (" + ",".join(cols_ok_admin) + ") VALUES (" + ",".join(["?"]*len(cols_ok_admin)) + ")", vals_ok_admin)
            message = "Enregistre ! Matricule : " + mat
        conn.commit()
    if request.args.get('edit'):
        cur.execute("SELECT * FROM etudiants_propres WHERE matricule=?", (request.args.get('edit'),)); edit = cur.fetchone()
    cur.execute("SELECT * FROM etudiants_propres ORDER BY matricule"); all_e = cur.fetchall()
    etus = [r for r in all_e if match_q(q, r['matricule'], r['nom'], r['gmail'], r['departement'], r['faculte'], r['niveau'])]
    cur.execute("SELECT COUNT(*) as nb FROM recours WHERE statut='En attente'"); nb_rec = cur.fetchone()['nb']; conn.close()
    auto = next_mat()
    fac_opt = "".join(["<option "+("selected" if edit and edit[3]==f else "")+">"+f+"</option>" for f in FACULTES])
    niv_opt = "".join(["<option "+("selected" if edit and edit[5]==n else "")+">"+n+"</option>" for n in NIVEAUX])
    lignes = ""
    for r in etus:
        try: ph = r['photo'] or ""
        except: ph = ""
        img = '<img src="/photo/etudiant/'+r['matricule']+'" style="width:42px;height:52px;object-fit:cover;border-radius:6px;border:1px solid #ccc">' if ph else '<div style="width:42px;height:52px;background:#EEE;border-radius:6px;text-align:center;line-height:52px;font-size:11px">Pas photo</div>'
        lignes += "<tr><td>"+img+"</td><td><b>"+(r['matricule'] or "")+"</b></td><td>"+(r['nom'] or "")+"</td><td>"+(r['faculte'] or "")+"<br>"+(r['departement'] or "")+"<br>"+(r['niveau'] or "")+"</td><td>"+(r['gmail'] or "")+"</td><td><a class='btn-mini edit' href='/admin?edit="+(r['matricule'] or "")+"'>Modifier</a><a class='btn-mini' style='background:#1A7A2E' href='/carte/"+(r['matricule'] or "")+"' target='_blank'>Voir Carte</a><form method='POST' style='display:inline'><input type='hidden' name='action' value='delete'><input type='hidden' name='matricule' value='"+(r['matricule'] or "")+"'><button class='btn-mini del' style='width:auto'>Supprimer</button></form></td></tr>"
    if not etus: lignes = "<tr><td colspan='6' style='text-align:center'>Aucun etudiant.</td></tr>"
    emat = edit['matricule'] if edit else auto; enom = edit['nom'] if edit else ""; egmail = edit['gmail'] if edit else ""; edept = edit['departement'] if edit else ""
    try: edate = edit['date_naissance'] if edit else ""; elieu = edit['lieu_naissance'] if edit else ""; enumc = edit['numero_carte'] if edit else ""
    except: edate=""; elieu=""; enumc=""
    titre = "Corriger Etudiant" if edit else "Panel Admin - UCBC"
    btn = "Sauvegarder la correction" if edit else "Ajouter Etudiant (Matricule auto)"
    info = '<p>Tu modifies <b>'+emat+'</b></p>' if edit else '<p>Prochain matricule = <b>'+auto+'</b></p>'
    ok = '<div class="alert alert-green">'+message+'</div>' if message else ""
    rec_alert = "<div class='alert alert-yellow'>"+str(nb_rec)+" recours en attente ! <a href='/admin/recours'>Voir</a></div>" if nb_rec>0 else ""
    h = STYLE + JS_FAC + header('admin') + back_top("/") + '<div class="wrap"><div style="display:flex;justify-content:space-between"><h2>Administration UCBC</h2><a href="/admin/logout" style="text-decoration:none"><button style="width:auto;padding:10px 16px;background:#DC2626">Deconnexion</button></a></div>' + rec_alert + '<div style="display:flex;gap:10px;margin:16px 0;flex-wrap:wrap"><a href="/admin" style="flex:1;text-decoration:none"><button>Etudiants</button></a><a href="/admin/preinscriptions" style="flex:1;text-decoration:none"><button class="blue">Pre-inscriptions</button></a><a href="/admin/enseignants" style="flex:1;text-decoration:none"><button class="blue">Enseignants</button></a><a href="/admin/cours" style="flex:1;text-decoration:none"><button class="blue">Cours</button></a><a href="/admin/horaire" style="flex:1;text-decoration:none"><button>Horaire</button></a><a href="/admin/notes" style="flex:1;text-decoration:none"><button class="navy">Notes</button></a><a href="/admin/recours" style="flex:1;text-decoration:none"><button class="blue">Recours / Jury ('+str(nb_rec)+')</button></a><a href="/admin/rattrapage" style="flex:1;text-decoration:none"><button>Rattrapage</button></a><a href="/admin/paie" style="flex:1;text-decoration:none"><button>Paie</button></a><a href="/jury/messagerie" style="flex:1;text-decoration:none"><button class="blue">Messagerie Jury - Enseignants</button></a></div>'
    h += '<div class="box"><h2>'+titre+'</h2>'+info+'<form method="post" enctype="multipart/form-data" style="background:#F8FAFC;padding:18px;border-radius:14px"><label>Matricule</label><input name="matricule" value="'+emat+'" readonly><label>Nom - Postnom - Prenom</label><input name="nom" value="'+enom+'" required><label>Gmail</label><input name="gmail" type="email" value="'+egmail+'" required><label>Faculte</label><select id="fac" name="faculte" onchange="updateDept(\'\')">'+fac_opt+'</select><label>Departement</label><select id="dept" name="departement"></select><label>Niveau</label><select name="niveau">'+niv_opt+'</select><label>Photo de l etudiant - choisir dans ses dossiers</label><input type="file" name="photo" accept="image/*"><label>Date de naissance - ex: 09/07/1995</label><input name="date_naissance" value="'+edate+'" placeholder="JJ/MM/AAAA"><label>Lieu de naissance - ex: Oicha</label><input name="lieu_naissance" value="'+elieu+'" placeholder="Ex: Oicha"><label>Numero Carte - ex: 7424</label><input name="numero_carte" value="'+enumc+'" placeholder="7424"><button class="green">'+btn+'</button></form>'+ok+'<h3>Liste UCBC ('+str(len(etus))+')</h3>'+search_bar(q,"Rechercher un etudiant...")+'<table><tr><th>Photo</th><th>Matricule</th><th>Nom</th><th>Fac / Dept / Niveau</th><th>Gmail</th><th>Action</th></tr>'+lignes+'</table></div></div><script>updateDept("'+edept+'");</script>'
    return render_template_string(h)
@app.route('/inscription', methods=['GET','POST'])
def inscription_publique():
    msg = ""
    if request.method == 'POST':
        conn = get_db(); cur = conn.cursor()
        try: cur.execute("CREATE TABLE IF NOT EXISTS preinscriptions (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, gmail TEXT, faculte TEXT, departement TEXT, niveau TEXT, date_naissance TEXT, lieu_naissance TEXT, telephone TEXT, statut TEXT DEFAULT 'En attente', date_envoi TEXT)")
        except: pass
        conn.commit()
        cur.execute("INSERT INTO preinscriptions (nom, gmail, faculte, departement, niveau, date_naissance, lieu_naissance, telephone, statut, date_envoi) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (request.form.get('nom','').strip(), request.form.get('gmail','').strip().lower(), request.form.get('faculte'), request.form.get('departement'), request.form.get('niveau'), request.form.get('date_naissance',''), request.form.get('lieu_naissance',''), request.form.get('telephone',''), 'En attente', datetime.now().strftime("%d/%m/%Y")))
        conn.commit(); conn.close()
        msg = "Demande envoyee ! L'administration va valider et te donner ton matricule."
    fac_opt = "".join(["<option>"+f+"</option>" for f in FACULTES])
    niv_opt = "".join(["<option>"+n+"</option>" for n in NIVEAUX])
    ok = '<div class="alert alert-green">'+msg+'</div>' if msg else ""
    h = STYLE + JS_FAC + header('inscription') + back_top("/") + '<div class="wrap"><div class="box" style="max-width:600px;margin:20px auto"><h2>📝 Inscription en ligne - UCBC</h2><p style="text-align:center;color:#475569">Remplis le formulaire, l\'admin te donnera ton matricule apres validation.</p>'+ok+'<form method="post"><label>Nom - Postnom - Prenom</label><input name="nom" required><label>Gmail</label><input name="gmail" type="email" required><label>Telephone / WhatsApp</label><input name="telephone" placeholder="Ex: +243 970 000 000"><label>Faculte</label><select id="fac" name="faculte" onchange="updateDept(\'\')">'+fac_opt+'</select><label>Departement</label><select id="dept" name="departement"></select><label>Niveau</label><select name="niveau">'+niv_opt+'</select><label>Date de naissance</label><input name="date_naissance" placeholder="JJ/MM/AAAA"><label>Lieu de naissance</label><input name="lieu_naissance" placeholder="Ex: Oicha"><button class="green">Envoyer ma demande</button></form></div></div><script>updateDept("");</script>'
    return render_template_string(h)

@app.route('/admin/preinscriptions', methods=['GET','POST'])
def admin_preinscriptions():
    if not is_admin(): return redirect("/admin/login")
    conn = get_db(); cur = conn.cursor()
    try: cur.execute("CREATE TABLE IF NOT EXISTS preinscriptions (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, gmail TEXT, faculte TEXT, departement TEXT, niveau TEXT, date_naissance TEXT, lieu_naissance TEXT, telephone TEXT, statut TEXT DEFAULT 'En attente', date_envoi TEXT)")
    except: pass
    conn.commit()
    msg = ""
    if request.method == 'POST':
        cur.execute("SELECT * FROM preinscriptions WHERE id=?", (request.form.get('id'),)); p = cur.fetchone()
        if p:
            nouveau_mat = next_mat()
            cur.execute("PRAGMA table_info(etudiants_propres)")
            cols = [r[1] for r in cur.fetchall()]
            toutes_valeurs = {
                'matricule': nouveau_mat,
                'nom': p['nom'],
                'gmail': p['gmail'],
                'faculte': p['faculte'],
                'departement': p['departement'],
                'niveau': p['niveau'],
                'date_inscription': datetime.now().strftime("%d/%m/%Y"),
                'date': datetime.now().strftime("%d/%m/%Y"),
                'photo': "",
                'date_naissance': p['date_naissance'],
                'lieu_naissance': p['lieu_naissance'],
                'numero_carte': nouveau_mat[-4:],
                'telephone': p['telephone'] if 'telephone' in p.keys() else "",
                'mot_de_passe': "1234",
                'password': "1234",
                'mdp': "1234",
                'statut': "Actif",
            }
            cols_ok = [c for c in cols if c in toutes_valeurs]
            vals_ok = [toutes_valeurs[c] for c in cols_ok]
            cur.execute("INSERT OR REPLACE INTO etudiants_propres (" + ",".join(cols_ok) + ") VALUES (" + ",".join(["?"]*len(cols_ok)) + ")", vals_ok)
            cur.execute("UPDATE preinscriptions SET statut='Valide' WHERE id=?", (p['id'],))
            conn.commit(); msg = "Valide ! Matricule donne : " + nouveau_mat
    cur.execute("SELECT * FROM preinscriptions WHERE statut='En attente' ORDER BY id DESC"); liste = cur.fetchall(); conn.close()
    lignes = ""
    for r in liste:
        lignes += "<tr><td><b>"+(r['nom'] or "")+"</b><br>"+(r['gmail'] or "")+"<br>"+(r['telephone'] or "")+"</td><td>"+(r['faculte'] or "")+"<br>"+(r['departement'] or "")+"<br>"+(r['niveau'] or "")+"</td><td><form method='POST' style='display:inline'><input type='hidden' name='id' value='"+str(r['id'])+"'><button class='btn-mini' style='background:#16A34A;width:auto'>Valider + Donner Matricule</button></form></td></tr>"
    if not lignes: lignes = "<tr><td colspan='3' style='text-align:center'>Aucune demande en attente.</td></tr>"
    h = STYLE + header('admin') + back_top("/admin") + '<div class="wrap"><div class="box"><h2>Pre-inscriptions en ligne</h2><p style="color:green;text-align:center"><b>'+msg+'</b></p><table><tr><th>Etudiant</th><th>Fac / Dept / Niveau</th><th>Action</th></tr>'+lignes+'</table></div></div>'
    return render_template_string(h)


@app.route('/admin/enseignants', methods=['GET','POST'])
def admin_enseignants():
    if not is_admin(): return redirect("/admin/login")
    q = request.args.get('q',''); msg = ""; edit = None
    conn = get_db(); cur = conn.cursor()
    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            cur.execute("DELETE FROM enseignants WHERE id=?", (request.form.get('id'),)); cur.execute("DELETE FROM affectations WHERE enseignant_id=?", (request.form.get('id'),)); msg = "Enseignant supprime"
        elif request.form.get('action') == 'add_affectation':
            cur.execute("INSERT INTO affectations (enseignant_id, faculte, departement, niveau, cours_id) VALUES (?,?,?,?,?)", (request.form.get('enseignant_id'), request.form.get('faculte'), request.form.get('departement'), request.form.get('niveau'), request.form.get('cours_id') if request.form.get('cours_id') else None)); msg = "Affectation ajoutee"
        else:
            dept_val = request.form.get('departement','') or "Informatique de Gestion"
            fac_val = request.form.get('faculte','') or "Sciences Economiques et de Gestion"
            niv_val = request.form.get('niveau','') or "L1"
                        # --- CORRIGE : on ne vide jamais le mot de passe si le champ est vide ---
            nouveau_mdp = request.form.get('mot_de_passe','').strip()
            if request.form.get('id'):
                if nouveau_mdp == "":
                    # L'admin n'a pas changé le mot de passe, on garde l'ancien
                    cur.execute("SELECT mot_de_passe FROM enseignants WHERE id=?", (request.form.get('id'),))
                    _old = cur.fetchone()
                    nouveau_mdp = _old[0] if _old else ""
                cur.execute("UPDATE enseignants SET nom=?, gmail=?, mot_de_passe=?, grade=?, faculte=?, departement=?, niveau=? WHERE id=?", (request.form.get('nom',''), request.form.get('gmail','').lower(), nouveau_mdp, request.form.get('grade',''), fac_val, dept_val, niv_val, request.form.get('id')))
                _eid = int(request.form.get('id')); msg = "Enseignant actualise ! Nouveau mot de passe actif."
            else:
                cur.execute("INSERT INTO enseignants (nom, gmail, mot_de_passe, grade, faculte, departement, niveau, date_creation) VALUES (?,?,?,?,?,?,?,?)", (request.form.get('nom',''), request.form.get('gmail','').lower(), nouveau_mdp, request.form.get('grade',''), fac_val, dept_val, niv_val, datetime.now().strftime("%d/%m/%Y")))
                _eid = cur.lastrowid
                cur.execute("INSERT INTO affectations (enseignant_id, faculte, departement, niveau) VALUES (?,?,?,?)", (_eid, fac_val, dept_val, niv_val))
                msg = "Enseignant cree ! Il peut se connecter."
            fph = request.files.get('photo')
            if fph and fph.filename != "":
                            
                try: cur.execute("UPDATE enseignants SET photo=? WHERE id=?", (_pn, _eid))
                except: pass
        conn.commit()
    if request.args.get('edit'):
        cur.execute("SELECT * FROM enseignants WHERE id=?", (request.args.get('edit'),)); edit = cur.fetchone()
    cur.execute("SELECT * FROM enseignants ORDER BY nom"); all_ens = cur.fetchall()
    liste = [r for r in all_ens if match_q(q, r['nom'], r['gmail'], r['grade'], r['departement'])]
    cur.execute("SELECT * FROM cours ORDER BY nom"); clist = cur.fetchall()
    cur.execute("SELECT * FROM affectations"); affs = cur.fetchall(); conn.close()
    fac_opt = "".join(["<option "+("selected" if edit and edit[5]==f else "")+">"+f+"</option>" for f in FACULTES])
    grade_opt = "".join(["<option "+("selected" if edit and edit[4]==g else "")+">"+g+"</option>" for g in GRADES])
    niv_opt = "".join(["<option "+("selected" if edit and edit[7]==n else "")+">"+n+"</option>" for n in NIVEAUX])
    lignes = ""
    for r in liste:
        aff_txt = "<br>".join(["<small>"+a['departement']+" - "+a['niveau']+"</small>" for a in affs if a['enseignant_id']==r['id']]) or r['departement']+" - "+r['niveau']
        lignes += "<tr><td><b>"+r['grade']+" "+r['nom']+"</b><br>"+r['gmail']+"<br>Mot de passe : "+r['mot_de_passe']+"</td><td>"+r['faculte']+"<br>"+aff_txt+"</td><td><div style='display:flex;gap:8px;flex-wrap:wrap;align-items:center;min-width:280px'><a class='btn-mini edit' style='padding:8px 12px;font-size:13px;font-weight:600;white-space:nowrap;text-decoration:none' href='/admin/enseignants?edit="+str(r['id'])+"'>Modifier</a><a class='btn-mini' style='background:#0D3B8C;padding:8px 12px;font-size:13px;font-weight:600;white-space:nowrap;text-decoration:none;color:white;border-radius:8px' href='/dashboard-enseignant/"+str(r['id'])+"'>Voir son espace</a><form method='POST' style='display:inline;margin:0'><input type='hidden' name='action' value='delete'><input type='hidden' name='id' value='"+str(r['id'])+"'><button class='btn-mini del' style='width:auto;padding:8px 12px;font-size:13px;font-weight:600;white-space:nowrap'>Supprimer</button></form></div></td></tr>"
    if not liste: lignes = "<tr><td colspan='3' style='text-align:center'>Aucun enseignant.</td></tr>"
    opt_cours = "".join(["<option value='"+str(c['id'])+"'>"+c['nom']+" - "+c['departement']+" - "+c['niveau']+"</option>" for c in clist])
    opt_ens = "".join(["<option value='"+str(r['id'])+"'>"+r['nom']+" - "+r['grade']+"</option>" for r in all_ens])
    id_hidden = '<input type="hidden" name="id" value="'+str(edit['id'])+'">' if edit else ""
    h = STYLE + JS_FAC + header('admin') + back_top("/admin") + '<div class="wrap"><div class="box"><h2>Admin - Enseignants</h2><p style="text-align:center;color:green"><b>' + msg + '</b></p><div style="background:#F3E8FF;border:2px solid #7C3AED;border-radius:12px;padding:16px"><h3>Ajouter / Modifier un Enseignant</h3><form method="POST" enctype="multipart/form-data">' + id_hidden + '<input name="nom" placeholder="Nom" value="'+(edit['nom'] if edit else "")+'" required><input name="gmail" type="email" placeholder="Gmail" value="'+(edit['gmail'] if edit else "")+'" required><input name="mot_de_passe" placeholder="Mot de passe" value="'+(edit['mot_de_passe'] if edit else "")+'" required><select name="grade">' + grade_opt + '</select><select id="fac" name="faculte" onchange="updateDept(\'\')">' + fac_opt + '</select><select id="dept" name="departement"></select><select name="niveau">' + niv_opt + '</select><label>Photo de l enseignant - choisir dans ses dossiers</label><input type="file" name="photo" accept="image/*"><button class="purple">Sauvegarder</button></form></div>'
    h += '<div style="background:#EFF6FF;border:2px solid #0D3B8C;border-radius:12px;padding:16px;margin-top:14px"><h3>Ajouter une affectation : Il enseigne aussi une autre promotion</h3><form method="POST"><input type="hidden" name="action" value="add_affectation"><select name="enseignant_id">' + opt_ens + '</select><select name="faculte">' + "".join(["<option>"+f+"</option>" for f in FACULTES]) + '</select><input name="departement" placeholder="Departement" required><select name="niveau">' + "".join(["<option>"+n+"</option>" for n in NIVEAUX]) + '</select><select name="cours_id"><option value="">Aucun cours precis</option>' + opt_cours + '</select><button>Ajouter cette affectation</button></form></div>'
    h += '<h3>Enseignants (' + str(len(liste)) + ')</h3>' + search_bar(q, "Rechercher un enseignant...") + '<table><tr><th>Enseignant + Grade + Connexion</th><th>Faculte / Promotions</th><th>Action</th></tr>' + lignes + '</table></div></div><script>updateDept("' + (edit['departement'] if edit else "") + '");</script>'
    return render_template_string(h)
@app.route('/admin/cours', methods=['GET','POST'])
def admin_cours():
    if not is_admin(): return redirect("/admin/login")
    q = request.args.get('q',''); msg = ""
    conn = get_db(); cur = conn.cursor()
    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            cur.execute("DELETE FROM cours WHERE id=?", (request.form.get('id'),)); cur.execute("DELETE FROM horaires WHERE cours_id=?", (request.form.get('id'),)); cur.execute("DELETE FROM notes WHERE cours_id=?", (request.form.get('id'),)); cur.execute("DELETE FROM cours_cibles WHERE cours_id=?", (request.form.get('id'),)); msg = "Cours supprime"
        else:
            cur.execute("INSERT INTO cours (nom, faculte, departement, niveau, prof, credits, salle, trimestre, annee) VALUES (?,?,?,?,?,?,?,?,?)", (request.form.get('nom'), request.form.get('faculte'), request.form.get('departement'), request.form.get('niveau'), request.form.get('prof'), int(request.form.get('credits',1)), request.form.get('salle'), request.form.get('trimestre'), "2026-2027"))
            new_id = cur.lastrowid
            cibles = request.form.getlist("cibles")
            if not cibles:
                cur.execute("INSERT INTO cours_cibles (cours_id, faculte, departement, niveau) VALUES (?,?,?,?)", (new_id, request.form.get('faculte'), request.form.get('departement'), request.form.get('niveau')))
            else:
                for cib in cibles:
                    parts = cib.split("|")
                    if len(parts) == 3: cur.execute("INSERT INTO cours_cibles (cours_id, faculte, departement, niveau) VALUES (?,?,?,?)", (new_id, parts[0], parts[1], parts[2]))
            msg = "Nouveau cours cree ! Cours d'ensemble pour " + str(len(cibles) if cibles else 1) + " promotion(s)."
        conn.commit()
    cur.execute("SELECT * FROM cours ORDER BY departement, niveau, nom"); allc = cur.fetchall()
    liste = [r for r in allc if match_q(q, r['nom'], r['prof'], r['departement'], r['salle'])]; conn.close()
    fac_opt = "".join(["<option>"+f+"</option>" for f in FACULTES]); niv_opt = "".join(["<option>"+n+"</option>" for n in NIVEAUX]); trim_opt = "".join(["<option>"+t+"</option>" for t in TRIMESTRES])
    cases = ""
    for f in FACULTES:
        for d in FACULTES[f]:
            for n in NIVEAUX:
                val = f + "|" + d + "|" + n
                cases += "<label style='display:block;font-weight:400;font-size:13px'><input type='checkbox' name='cibles' value='" + val + "' style='width:auto'> " + f + " - " + d + " - " + n + "</label>"
    lignes = "".join(["<tr><td><b>"+r['nom']+"</b></td><td>"+r['departement']+" - "+r['niveau']+" - "+r['trimestre']+"</td><td>"+r['prof']+"</td><td>"+str(r['credits'])+" crdts</td><td>"+r['salle']+"</td><td><form method='POST'><input type='hidden' name='action' value='delete'><input type='hidden' name='id' value='"+str(r['id'])+"'><button class='btn-mini del' style='width:auto'>Supprimer</button></form></td></tr>" for r in liste]) or "<tr><td colspan='6' style='text-align:center'>Aucun cours.</td></tr>"
    h = STYLE + JS_FAC + header('admin') + back_top("/admin") + '<div class="wrap"><div class="box"><h2>Admin - Cours</h2><div style="background:#EFF6FF;border:2px solid #0D3B8C;border-radius:12px;padding:16px"><h3>Ajouter un Cours</h3><form method="POST"><input name="nom" placeholder="Nom du cours" required><select id="fac" name="faculte" onchange="updateDept(\'\')">' + fac_opt + '</select><select id="dept" name="departement"></select><select name="niveau">' + niv_opt + '</select><input name="prof" placeholder="Prof" required><input name="credits" type="number" placeholder="Credits" required><input name="salle" placeholder="Salle" required><select name="trimestre">' + trim_opt + '</select><label>Cours d ensemble ? Coche toutes les promotions qui font ce cours ensemble</label><div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:10px;padding:12px;max-height:180px;overflow:auto">' + cases + '</div><button class="green">Ajouter ce Cours</button></form></div><p style="text-align:center;color:green"><b>' + msg + '</b></p><h3>Cours deja crees (' + str(len(liste)) + ')</h3>' + search_bar(q, "Rechercher un cours...") + '<table><tr><th>Cours</th><th>Dept / Niveau</th><th>Prof</th><th>Credits</th><th>Salle</th><th>Action</th></tr>' + lignes + '</table></div></div><script>updateDept("");</script>'
    return render_template_string(h)
# ============================================================
# --- ADMIN : HORAIRE - 1 SEULE TABLE POUR TOUS ---
# ============================================================
@app.route('/admin/horaire', methods=['GET','POST'])
def admin_horaire():
    if not is_admin(): return redirect("/login-admin")
    msg = ""
    conn = get_db(); cur = conn.cursor()

    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            cur.execute("DELETE FROM horaires WHERE id=?", (request.form.get('id'),)); msg = "Horaire supprime. L'enseignant et l'etudiant ne le voient plus."
        elif request.form.get('action') == 'edit':
            # --- MODIFICATION : ca se repercute directement chez l'enseignant car c'est la meme ligne ---
            cur.execute("UPDATE horaires SET cours_id=?, enseignant_id=?, jour=?, heure_debut=?, heure_fin=?, salle=? WHERE id=?",
                        (request.form.get('cours_id'), request.form.get('enseignant_id'), request.form.get('jour'),
                         request.form.get('heure_debut'), request.form.get('heure_fin'), request.form.get('salle'),
                         request.form.get('id'))); msg = "Horaire modifie. L'enseignant voit la nouvelle version."
        else:
            # --- CREATION : on enregistre le cours + l'enseignant en meme temps ---
            cur.execute("INSERT INTO horaires (cours_id, enseignant_id, jour, heure_debut, heure_fin, salle) VALUES (?,?,?,?,?,?)",
                        (request.form.get('cours_id'), request.form.get('enseignant_id'), request.form.get('jour'),
                         request.form.get('heure_debut'), request.form.get('heure_fin'), request.form.get('salle')))
            msg = "Horaire cree. L'enseignant et les etudiants le voient deja."
        conn.commit()

    cur.execute("SELECT * FROM cours ORDER BY nom"); clist = cur.fetchall()
    cur.execute("SELECT * FROM enseignants ORDER BY nom"); elist = cur.fetchall()
    cur.execute("SELECT horaires.*, cours.nom as cours_nom, cours.departement as cours_dept, cours.niveau as cours_niv, enseignants.nom as ens_nom, enseignants.grade as ens_grade FROM horaires LEFT JOIN cours ON horaires.cours_id=cours.id LEFT JOIN enseignants ON horaires.enseignant_id=enseignants.id ORDER BY horaires.id DESC")
    liste = cur.fetchall(); conn.close()

    opt_cours = "".join(["<option value='"+str(r['id'])+"'>"+r['nom']+" - "+r['departement']+" - "+r['niveau']+"</option>" for r in clist])
    opt_ens = "".join(["<option value='"+str(r['id'])+"'>"+r['grade']+" "+r['nom']+"</option>" for r in elist])
    opt_jour = "".join(["<option>"+j+"</option>" for j in ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']])

    lignes = ""
    for r in liste:
        lignes += "<tr><td><b>"+(r['cours_nom'] or "")+"</b><br>"+(r['cours_dept'] or "")+" - "+(r['cours_niv'] or "")+"<br><small>Ens: "+(r['ens_grade'] or "")+" "+(r['ens_nom'] or "-")+"</small></td><td>"+(r['jour'] or "")+"</td><td>"+(r['heure_debut'] or "")+" - "+(r['heure_fin'] or "")+"</td><td><b>"+(r['salle'] or "")+"</b></td><td><form method='POST'><input type='hidden' name='action' value='delete'><input type='hidden' name='id' value='"+str(r['id'])+"'><button class='btn-mini del' style='width:auto'>Supprimer</button></form></td></tr>"
    if not liste: lignes = "<tr><td colspan='5' style='text-align:center'>Aucun horaire.</td></tr>"

       # --- Creneaux horaires fixes : 07:00 a 17:00 ---
    creneaux = ["07:00","08:00","09:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00"]
    opt_debut = "".join([f'<option value="{x}">{x}</option>' for x in creneaux])
    opt_fin = "".join([f'<option value="{x}">{x}</option>' for x in creneaux])

    h = STYLE + header('admin') + back_top("/dashboard-admin") + '<div class="wrap"><div class="box"><h2>Horaire - Admin (1 seule version pour tous)</h2><p style="text-align:center;color:green"><b>'+msg+'</b></p>'
    h += '<div style="background:#EFF6FF;border:2px solid #0D3B8C;border-radius:12px;padding:16px"><h3>Ajouter un horaire</h3><form method="POST"><select name="cours_id">'+opt_cours+'</select><select name="enseignant_id">'+opt_ens+'</select><select name="jour">'+opt_jour+'</select>'
    h += '<label>Heure debut</label><select name="heure_debut" required>' + opt_debut + '</select>'
    h += '<label>Heure fin</label><select name="heure_fin" required>' + opt_fin + '</select>'
    h += '<input name="salle" placeholder="Salle ex: Salle 3" required><button>Ajouter - Visible chez Enseignant + Etudiant</button></form></div>'
    h += '<h3>Modifier un horaire (meme ligne, repercussion immediate)</h3><form method="POST"><input type="hidden" name="action" value="edit"><input name="id" type="number" placeholder="ID de l\'horaire a modifier" required><select name="cours_id">'+opt_cours+'</select><select name="enseignant_id">'+opt_ens+'</select><select name="jour">'+opt_jour+'</select>'
    h += '<label>Nouvelle heure debut</label><select name="heure_debut" required>' + opt_debut + '</select>'
    h += '<label>Nouvelle heure fin</label><select name="heure_fin" required>' + opt_fin + '</select>'
    h += '<input name="salle" placeholder="Nouvelle salle" required><button class="green">Modifier</button></form>'
    h += '<h3>Tous les horaires</h3><table><tr><th>Cours / Enseignant</th><th>Jour</th><th>Heure</th><th>Salle</th><th>Action</th></tr>'+lignes+'</table></div></div>'
    return render_template_string(h)

@app.route('/photo/etudiant/<path:mat>')
def photo_etudiant(mat):
    import os
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT photo FROM etudiants_propres WHERE matricule=?", (mat,))
    r = cur.fetchone(); conn.close()
    base = os.path.dirname(os.path.abspath(__file__))
    photo = ""
    try:
        photo = r['photo'] if r else ""
    except:
        photo = r[0] if r else ""
    if photo:
        # On cherche dans tous les dossiers possibles
        for dos in [os.path.join(base, "uploads"), os.path.join(base, "photos"), os.path.join(base, "static", "photos"), base]:
            chemin = os.path.join(dos, photo)
            if os.path.exists(chemin):
                return send_file(chemin)
        # Si photo = juste un nom sans dossier, essaie aussi avec le matricule
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            chemin = os.path.join(base, "uploads", mat.replace("/", "_") + ext)
            if os.path.exists(chemin):
                return send_file(chemin)
    # Sinon, logo
    logo = os.path.join(base, "logo_ucbc.png")
    if os.path.exists(logo):
        return send_file(logo)
    return "Photo introuvable", 404

@app.route('/carte/<path:mat>')
def carte_etudiant(mat):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT * FROM etudiants_propres WHERE matricule=?", (mat,))
    row = cur.fetchone(); conn.close()
    if not row:
        return "Etudiant introuvable"
    e = dict(row)
    try:
        date_n = e.get('date_naissance') or "---"; lieu_n = e.get('lieu_naissance') or "---"; num_c = e.get('numero_carte') or mat[-4:]
    except:
        date_n = "---"; lieu_n = "---"; num_c = mat[-4:]

    # --- PHOTO CORRIGEE ---
    photo_nom = (e.get('photo') or e.get('photo_path') or '').strip()
    if photo_nom:
        photo_url = '/uploads/' + photo_nom.replace('\\','/').split('/')[-1]
    else:
        photo_url = '/photo/etudiant/' + mat

    h = STYLE + header('etudiant') + back_top("/dashboard/"+mat) + '<div class="wrap"><div class="no-print" style="text-align:center;margin-bottom:12px"><button onclick="window.print()" style="width:auto;padding:12px 28px;background:#0A1931">Imprimer ma Carte</button></div>'
    h += '<div style="width:560px;max-width:100%;margin:0 auto;background:white;border:2px solid #C9A227;border-radius:14px;overflow:hidden">'
    h += '<div style="display:flex;align-items:center;gap:10px;padding:10px 14px;border-bottom:3px solid #C9A227"><img src="/logo_ucbc.png" style="width:62px;height:62px;object-fit:contain"><div style="flex:1;text-align:center"><div style="font-weight:900;font-size:19px;line-height:1.1;color:#0A1931">UNIVERSITE CHRETIENNE<br>BILINGUE DU CONGO</div><div style="color:#0D3B8C;font-size:12px">www.ci-ucbc.edu.cd</div></div><img src="/static/drapeau_rdc.png" onerror="this.onerror=null;this.src=\'/drapeau_rdc.png\'" style="width:62px;height:45px;object-fit:cover;border:1px solid #C9A227;border-radius:4px"></div>'
    h += '<div style="background:#1A7A2E;color:white;text-align:center;font-weight:900;font-size:20px;padding:8px">CARTE D ETUDIANT ' + str(num_c) + '</div>'
    h += '<div style="display:flex;gap:14px;padding:14px"><div style="width:135px;text-align:center"><div style="font-size:11px;color:#555">||||||||||||||||||||<br>' + mat + '</div><img src="' + photo_url + '" onerror="this.onerror=null;this.src=\'/logo_ucbc.png\'" style="width:120px;height:150px;object-fit:cover;border:2px solid #0A1931;border-radius:6px;background:#EEE"></div>'
    h += '<div style="flex:1"><div style="font-weight:900;font-size:21px;text-transform:uppercase;line-height:1.2">' + (e.get('nom') or "") + '</div><div style="font-size:15px;margin-top:10px"><b>Faculte :</b> ' + (e.get('faculte') or "") + '</div><div style="font-size:15px"><b>Departement :</b> ' + (e.get('departement') or "") + ' - ' + (e.get('niveau') or "") + '</div><div style="font-size:15px;margin-top:10px"><b>Ne(e) a ' + lieu_n + ' Le ' + date_n + '</b></div><div style="font-size:15px;margin-top:6px"><b>Matricule :</b> ' + mat + '</div><div style="font-size:13px;margin-top:14px">Fait a Beni, le 01/02/2024</div><div style="margin-top:16px;text-align:right"><div style="font-size:13px;font-weight:700">CT BORA UZIMA Innocent, SGAC</div><div style="font-size:22px;font-style:italic;color:#0D3B8C;margin-top:6px">Signature</div><div style="font-size:11px;color:#0D3B8C;border:1px solid #0D3B8C;display:inline-block;padding:4px 8px;border-radius:50%;margin-top:6px">UCBC - BENI</div></div></div></div></div>'
    h += '<p style="text-align:center;font-size:12px;color:#666;margin-top:10px">Cette carte est strictement personnelle. En cas de perte, priere de la retourner a l UCBC Beni.</p></div>'
    return render_template_string(h)

@app.route('/admin/notes', methods=['GET','POST'])
def admin_notes():
    if not is_admin(): return redirect("/admin/login")
    q = request.args.get('q',''); msg = ""
    conn = get_db(); cur = conn.cursor()
    # --- JURY : on ajoute les 2 colonnes si elles n'existent pas encore ---
    try: cur.execute("ALTER TABLE notes ADD COLUMN statut TEXT DEFAULT 'brouillon'")
    except: pass
    try: cur.execute("ALTER TABLE notes ADD COLUMN phase TEXT DEFAULT 'normale'")
    except: pass
    conn.commit()

    # --- 1. ENREGISTRER LES NOTES (Enseignant / Admin) ---
    if request.method == 'POST' and request.form.get('action') == 'save_notes':
        cid = request.form.get('cours_id'); mats = request.form.getlist("matricule_list"); vals = request.form.getlist("note_val")
        for m, n in zip(mats, vals):
            if n.strip() != "":
                cur.execute("SELECT note_originale, statut FROM notes WHERE matricule=? AND cours_id=?", (m, cid)); ex = cur.fetchone()
                orig = ex['note_originale'] if ex and ex['note_originale'] is not None else float(n)
                # Si la note etait deja publiee, on ne la re-publie pas tout seul, on la remet en "soumis_jury" pour re-validation
                # Si c'est une nouvelle note, elle arrive en "soumis_jury"
                cur.execute("INSERT INTO notes (matricule, cours_id, note, note_originale, date_ajout, statut, phase) VALUES (?,?,?,?,?, 'soumis_jury', 'normale') ON CONFLICT(matricule, cours_id) DO UPDATE SET note=excluded.note, note_originale=COALESCE(notes.note_originale, excluded.note_originale), statut='soumis_jury', phase='normale'", (m, cid, float(n), orig, datetime.now().strftime("%d/%m/%Y")))
        conn.commit(); msg = "Notes enregistrees ! Elles sont maintenant en attente du Jury (soumis_jury)."

    # --- 2. SUPPRIMER UNE NOTE ---
    if request.method == 'POST' and request.form.get('action') == 'delete_note':
        cur.execute("DELETE FROM notes WHERE matricule=? AND cours_id=?", (request.form.get('matricule'), request.form.get('cours_id'))); conn.commit(); msg = "Note supprimee."

        # --- 3. LE JURY : VALIDER ET PUBLIER PAR PHASE ---
    if request.method == 'POST' and request.form.get('action') in ['valider_jury','publie_normale','publie_recours','publie_rattrapage','depublier']:
        cid2 = request.form.get('cours_id')
        act = request.form.get('action')
        if act == 'valider_jury':
            cur.execute("UPDATE notes SET statut='valide_jury' WHERE cours_id=? AND statut IN ('soumis_jury','brouillon')", (cid2,)); msg = "Jury : Cotes validees ! Pret a publier. ("+str(cur.rowcount)+" cote(s) validee(s))"
        elif act == 'publie_normale':
            cur.execute("UPDATE notes SET statut='publie_normale', phase='normale' WHERE cours_id=? AND statut IN ('valide_jury','soumis_jury','brouillon')", (cid2,)); msg = "PUBLIE : Session Normale. Les etudiants voient leurs cotes. ("+str(cur.rowcount)+" cote(s) publiee(s))"
        elif act == 'publie_recours':
            cur.execute("UPDATE notes SET statut='publie_recours', phase='recours' WHERE cours_id=? AND statut IN ('valide_jury','soumis_jury','brouillon','publie_normale')", (cid2,)); msg = "PUBLIE : Apres Recours. ("+str(cur.rowcount)+" cote(s))"
        elif act == 'publie_rattrapage':
            cur.execute("UPDATE notes SET statut='publie_rattrapage', phase='rattrapage' WHERE cours_id=? AND statut IN ('valide_jury','soumis_jury','brouillon','publie_normale','publie_recours')", (cid2,)); msg = "PUBLIE : Apres Rattrapage. ("+str(cur.rowcount)+" cote(s))"
        elif act == 'depublier':
            cur.execute("UPDATE notes SET statut='valide_jury' WHERE cours_id=? AND statut LIKE 'publie_%'", (cid2,)); msg = "De-publie : les etudiants ne voient plus, retour en Jury. ("+str(cur.rowcount)+" cote(s))"
        conn.commit()

    cur.execute("SELECT * FROM cours ORDER BY nom"); clist = cur.fetchall()
    sel = request.args.get('cours_id') or (str(clist[0]['id']) if clist else "")
    csel = None; etus = []
    if sel:
        cur.execute("SELECT * FROM cours WHERE id=?", (sel,)); csel = cur.fetchone()
        if csel:
            cur.execute("SELECT * FROM etudiants_propres"); alle = cur.fetchall()
            etus = sorted([e for e in alle if cours_visible_pour(int(sel), e['departement'], e['niveau']) and match_q(q, e['nom'], e['matricule'])], key=lambda x: x['matricule'])
    # --- Statut actuel de ce cours pour le Jury ---
    statut_cours = "Aucune cote"
    if sel:
        cur.execute("SELECT statut, COUNT(*) as nb FROM notes WHERE cours_id=? GROUP BY statut", (sel,)); stats = cur.fetchall()
        if stats:
            statut_cours = " | ".join([s['statut']+" : "+str(s['nb']) for s in stats])
    conn.close()
    if not clist: return render_template_string(STYLE + header('admin') + back_top("/admin") + '<div class="wrap"><div class="box"><h2>Notes</h2><p>Aucun cours.</p></div></div>')
    opt = "".join(["<option value='"+str(r['id'])+"' "+("selected" if str(r['id'])==str(sel) else "")+">"+r['nom']+" - "+r['departement']+" - "+r['niveau']+"</option>" for r in clist])
    lignes = ""; conn2 = get_db(); cur2 = conn2.cursor()
    for e in etus:
        cur2.execute("SELECT note, statut FROM notes WHERE matricule=? AND cours_id=?", (e['matricule'], sel)); row = cur2.fetchone()
        val = row['note'] if row else ""; pt = str(pct(val))+"%" if row else "--%"
        st = row['statut'] if row and row['statut'] else "brouillon"
        # Petite couleur pour voir ou on en est
        coul = {"brouillon":"#6B7280","soumis_jury":"#F59E0B","valide_jury":"#0D3B8C","publie_normale":"#16A34A","publie_recours":"#7C3AED","publie_rattrapage":"#DC2626"}.get(st, "#6B7280")
        lignes += "<tr><td><b>"+e['matricule']+"</b><br>"+e['nom']+"</td><td><input type='hidden' name='matricule_list' value='"+e['matricule']+"'><input type='number' step='0.5' min='0' max='20' name='note_val' value='"+str(val)+"' placeholder='Note /20'></td><td><b>"+pt+"</b><br><small style='background:"+coul+";color:white;padding:2px 6px;border-radius:10px'>"+st+"</small></td><td><form method='POST'><input type='hidden' name='action' value='delete_note'><input type='hidden' name='matricule' value='"+e['matricule']+"'><input type='hidden' name='cours_id' value='"+str(sel)+"'><button class='btn-mini del' style='width:auto'>Supprimer</button></form></td></tr>"
    conn2.close()
    if not etus: lignes = "<tr><td colspan='4' style='text-align:center'>Aucun etudiant.</td></tr>"
    info = "<h3>"+csel['nom']+" - "+csel['departement']+" - "+csel['niveau']+"</h3><p>Les cotes deposees par l'enseignant apparaissent ici. Le Jury les valide.</p>" if csel else ""
    # --- BOUTONS DU JURY ---
    jury_box = '<div style="background:#FFFBEB;border:2px solid #F59E0B;border-radius:12px;padding:14px;margin-top:14px"><h3 style="margin:0">JURY - Deliberation & Publication</h3><p style="margin:6px 0"><b>Statut actuel de ce cours :</b> '+statut_cours+'</p><p style="font-size:13px;color:#92400E">Ordre a suivre : 1. Valider -> 2. Publier Normale -> 3. Publier Apres Recours -> 4. Publier Apres Rattrapage</p><div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">'
    jury_box += '<form method="POST" style="margin:0"><input type="hidden" name="action" value="valider_jury"><input type="hidden" name="cours_id" value="'+str(sel)+'"><button style="background:#0D3B8C;color:white;padding:10px 14px;border:none;border-radius:8px;font-weight:600;cursor:pointer">1. Valider par le Jury</button></form>'
    jury_box += '<form method="POST" style="margin:0"><input type="hidden" name="action" value="publie_normale"><input type="hidden" name="cours_id" value="'+str(sel)+'"><button style="background:#16A34A;color:white;padding:10px 14px;border:none;border-radius:8px;font-weight:600;cursor:pointer">2. Publier Session Normale</button></form>'
    jury_box += '<form method="POST" style="margin:0"><input type="hidden" name="action" value="publie_recours"><input type="hidden" name="cours_id" value="'+str(sel)+'"><button style="background:#7C3AED;color:white;padding:10px 14px;border:none;border-radius:8px;font-weight:600;cursor:pointer">3. Publier Apres Recours</button></form>'
    jury_box += '<form method="POST" style="margin:0"><input type="hidden" name="action" value="publie_rattrapage"><input type="hidden" name="cours_id" value="'+str(sel)+'"><button style="background:#DC2626;color:white;padding:10px 14px;border:none;border-radius:8px;font-weight:600;cursor:pointer">4. Publier Apres Rattrapage</button></form>'
    jury_box += '<form method="POST" style="margin:0"><input type="hidden" name="action" value="depublier"><input type="hidden" name="cours_id" value="'+str(sel)+'"><button style="background:#6B7280;color:white;padding:10px 14px;border:none;border-radius:8px;font-weight:600;cursor:pointer">De-publier (Cacher)</button></form>'
    jury_box += '</div></div>'
    h = STYLE + header('admin') + back_top("/admin") + '<div class="wrap"><div class="box"><h2>Admin / Jury - Notes</h2><form method="GET" style="background:#EFF6FF;padding:14px;border-radius:12px"><select name="cours_id" onchange="this.form.submit()">' + opt + '</select></form>' + info + search_bar(q, "Rechercher un etudiant...") + '<form method="POST"><input type="hidden" name="action" value="save_notes"><input type="hidden" name="cours_id" value="' + str(sel) + '"><table><tr><th>Etudiant</th><th>Cote /20</th><th>% + Statut</th><th>Action</th></tr>' + lignes + '</table><button class="green" style="margin-top:14px">Enregistrer / Actualiser</button></form>' + jury_box + '<p style="text-align:center;color:green"><b>' + msg + '</b></p></div></div>'
    return render_template_string(h)
@app.route('/admin/recours', methods=['GET','POST'])
def admin_recours():
    if not is_admin(): return redirect("/admin/login")
    q = request.args.get('q',''); msg = ""
    conn = get_db(); cur = conn.cursor()
    if request.method == 'POST':
        rid = request.form.get('id'); act = request.form.get('action'); rep = request.form.get('reponse_jury','')
        cur.execute("SELECT * FROM recours WHERE id=?", (rid,)); r = cur.fetchone()
        if r and act == 'accepter':
            cur.execute("UPDATE notes SET note=? WHERE matricule=? AND cours_id=?", (r['note_reclamee'], r['matricule'], r['cours_id'])); cur.execute("UPDATE recours SET statut='Accepte', reponse_jury=? WHERE id=?", (rep or "Accepte. Corrigee.", rid)); msg = "Recours accepte ! Cote corrigee."
        elif r and act == 'refuser':
            cur.execute("UPDATE recours SET statut='Refuse', reponse_jury=? WHERE id=?", (rep or "Refuse. Preuve insuffisante.", rid)); msg = "Recours refuse."
        elif r and act == 'annuler_acceptation':
            cur.execute("SELECT note_originale FROM notes WHERE matricule=? AND cours_id=?", (r['matricule'], r['cours_id'])); n = cur.fetchone()
            orig = n['note_originale'] if n and n['note_originale'] is not None else r['note_affichee']
            cur.execute("UPDATE notes SET note=? WHERE matricule=? AND cours_id=?", (orig, r['matricule'], r['cours_id'])); cur.execute("UPDATE recours SET statut='En attente', reponse_jury='Acceptation annulee. Cote restauree.' WHERE id=?", (rid,)); msg = "Acceptation annulee ! Cote restauree a " + str(orig)
        elif r and act == 'delete_recours':
            cur.execute("SELECT note_originale FROM notes WHERE matricule=? AND cours_id=?", (r['matricule'], r['cours_id'])); n = cur.fetchone()
            if r['statut'] == 'Accepte' and n: cur.execute("UPDATE notes SET note=? WHERE matricule=? AND cours_id=?", (n['note_originale'] if n['note_originale'] is not None else r['note_affichee'], r['matricule'], r['cours_id']))
            cur.execute("DELETE FROM recours WHERE id=?", (rid,)); msg = "Recours supprime. Cote restauree si necessaire."
        conn.commit()
    cur.execute("SELECT recours.*, cours.nom as cours_nom, etudiants_propres.nom as etu_nom FROM recours JOIN cours ON recours.cours_id=cours.id JOIN etudiants_propres ON recours.matricule=etudiants_propres.matricule ORDER BY CASE WHEN recours.statut='En attente' THEN 0 ELSE 1 END, recours.id DESC"); allr = cur.fetchall()
    liste = [r for r in allr if match_q(q, r['etu_nom'], r['matricule'], r['cours_nom'], r['statut'], r['motif'])]; conn.close()
    lignes = ""
    for r in liste:
        badge = "En attente"
        if r['statut'] == 'Accepte': badge = "Accepte"
        if r['statut'] == 'Refuse': badge = "Refuse"
        preuve = ""
        if r['preuve_fichier']: preuve = '<a href="/fichier/preuves/'+r['preuve_fichier']+'" target="_blank">Voir preuve</a>'
        if r['statut'] == 'En attente': act_html = "<form method='POST'><input type='hidden' name='id' value='"+str(r['id'])+"'><input name='reponse_jury' placeholder='Reponse Jury'><button class='green' name='action' value='accepter' style='margin:4px 0'>Accepter vers "+str(r['note_reclamee'])+"</button><button class='red' name='action' value='refuser'>Refuser</button><button class='gray' name='action' value='delete_recours'>Supprimer</button></form>"
        elif r['statut'] == 'Accepte': act_html = "<p>"+(r['reponse_jury'] or "")+"</p><form method='POST'><input type='hidden' name='id' value='"+str(r['id'])+"'><button class='orange' name='action' value='annuler_acceptation'>Annuler l'acceptation (test)</button><button class='gray' name='action' value='delete_recours'>Supprimer</button></form>"
        else: act_html = "<p>"+(r['reponse_jury'] or "")+"</p><form method='POST'><input type='hidden' name='id' value='"+str(r['id'])+"'><button class='gray' name='action' value='delete_recours'>Supprimer</button></form>"
        lignes += "<tr><td><b>"+r['etu_nom']+"</b><br>"+r['matricule']+"<br>"+r['date_envoi']+"</td><td><b>"+r['cours_nom']+"</b></td><td>"+str(r['note_affichee'])+" / 20</td><td><b>"+str(r['note_reclamee'])+" / 20</b></td><td>"+r['motif']+"<br>"+preuve+"</td><td>"+badge+"</td><td>"+act_html+"</td></tr>"
    if not liste: lignes = "<tr><td colspan='7' style='text-align:center'>Aucun recours.</td></tr>"
    h = STYLE + header('admin') + back_top("/admin") + '<div class="wrap"><div class="box"><h2>Jury - Recours</h2><p style="text-align:center;color:green"><b>' + msg + '</b></p>' + search_bar(q, "Rechercher un recours...") + '<table><tr><th>Etudiant</th><th>Cours</th><th>Cote affichee</th><th>Cote reclamee</th><th>Motif + Preuve</th><th>Statut</th><th>Decision Jury</th></tr>' + lignes + '</table></div></div>'
    return render_template_string(h)
@app.route('/admin/rattrapage', methods=['GET','POST'])
def admin_rattrapage():
    if not is_admin(): return redirect("/admin/login")
    q = request.args.get('q',''); msg = ""
    conn = get_db(); cur = conn.cursor()
    if request.method == 'POST' and request.form.get('action') == 'save_ratt':
        cid = request.form.get('cours_id'); mats = request.form.getlist("matricule_list"); vals = request.form.getlist("note_val")
        for m, n in zip(mats, vals):
            if n.strip() != "": cur.execute("INSERT INTO rattrapages (matricule, cours_id, note_rattrapage, date_ajout) VALUES (?,?,?,?) ON CONFLICT(matricule, cours_id) DO UPDATE SET note_rattrapage=excluded.note_rattrapage", (m, cid, float(n), datetime.now().strftime("%d/%m/%Y")))
        conn.commit(); msg = "Notes de rattrapage enregistrees !"
    if request.method == 'POST' and request.form.get('action') == 'delete_ratt':
        cur.execute("DELETE FROM rattrapages WHERE matricule=? AND cours_id=?", (request.form.get('matricule'), request.form.get('cours_id'))); conn.commit(); msg = "Note de rattrapage supprimee."
    cur.execute("SELECT * FROM cours ORDER BY nom"); clist = cur.fetchall()
    sel = request.args.get('cours_id') or (str(clist[0]['id']) if clist else "")
    csel = None; etus = []
    if sel:
        cur.execute("SELECT * FROM cours WHERE id=?", (sel,)); csel = cur.fetchone()
        if csel:
            cur.execute("SELECT * FROM etudiants_propres"); alle = cur.fetchall()
            etus = sorted([e for e in alle if cours_visible_pour(int(sel), e['departement'], e['niveau']) and match_q(q, e['nom'], e['matricule'])], key=lambda x: x['matricule'])
    conn.close()
    if not clist: return render_template_string(STYLE + header('admin') + back_top("/admin") + '<div class="wrap"><div class="box"><h2>Rattrapage</h2><p>Aucun cours.</p></div></div>')
    opt = "".join(["<option value='"+str(r['id'])+"' "+("selected" if str(r['id'])==str(sel) else "")+">"+r['nom']+" - "+r['departement']+" - "+r['niveau']+"</option>" for r in clist])
    lignes = ""; conn2 = get_db(); cur2 = conn2.cursor()
    for e in etus:
        cur2.execute("SELECT note FROM notes WHERE matricule=? AND cours_id=?", (e['matricule'], sel)); row = cur2.fetchone(); no = row['note'] if row else "Pas note"
        cur2.execute("SELECT note_rattrapage FROM rattrapages WHERE matricule=? AND cours_id=?", (e['matricule'], sel)); rr = cur2.fetchone(); val = rr['note_rattrapage'] if rr else ""
        lignes += "<tr><td><b>"+e['matricule']+"</b><br>"+e['nom']+"</td><td>"+str(no)+" / 20</td><td><input type='hidden' name='matricule_list' value='"+e['matricule']+"'><input type='number' step='0.5' min='0' max='20' name='note_val' value='"+str(val)+"' placeholder='Note rattrapage'></td><td><form method='POST'><input type='hidden' name='action' value='delete_ratt'><input type='hidden' name='matricule' value='"+e['matricule']+"'><input type='hidden' name='cours_id' value='"+str(sel)+"'><button class='btn-mini del' style='width:auto'>Supprimer</button></form></td></tr>"
    conn2.close()
    info = "<h3>"+csel['nom']+" - "+csel['departement']+" - "+csel['niveau']+"</h3>" if csel else ""
    h = STYLE + header('admin') + back_top("/admin") + '<div class="wrap"><div class="box"><h2>Admin - Rattrapage</h2><form method="GET" style="background:#EFF6FF;padding:14px;border-radius:12px"><select name="cours_id" onchange="this.form.submit()">' + opt + '</select></form>' + info + search_bar(q, "Rechercher un etudiant...") + '<form method="POST"><input type="hidden" name="action" value="save_ratt"><input type="hidden" name="cours_id" value="' + str(sel) + '"><table><tr><th>Etudiant</th><th>Cote Ordinaire</th><th>Cote Rattrapage</th><th>Action</th></tr>' + lignes + '</table><button class="green" style="margin-top:14px">Enregistrer</button></form><p style="text-align:center;color:green"><b>' + msg + '</b></p></div></div>'
    return render_template_string(h)
@app.route('/admin/paie', methods=['GET','POST'])
def admin_paie():
    if not is_admin():
        return redirect("/admin/login")
    q = request.args.get('q',''); msg = ""; edit_p = None
    conn = get_db(); cur = conn.cursor()
    if request.method == 'POST':
        if request.form.get('action') == 'delete':
            cur.execute("DELETE FROM paiements WHERE id=?", (request.form.get('id'),)); msg = "Paiement supprime."
        elif request.form.get('action') == 'update':
            cur.execute("UPDATE paiements SET matricule=?, montant_total=?, montant_paye=?, motif=? WHERE id=?", (request.form.get('matricule'), float(request.form.get('total',0)), float(request.form.get('paye',0)), request.form.get('motif'), request.form.get('id'))); msg = "Paiement actualise !"
        elif request.form.get('action') == 'add':
            cur.execute("INSERT INTO paiements (numero_paie, matricule, montant_total, montant_paye, date_paiement, motif) VALUES (?,?,?,?,?,?)", (next_paie(), request.form.get('matricule'), float(request.form.get('total',0)), float(request.form.get('paye',0)), datetime.now().strftime("%d/%m/%Y"), request.form.get('motif'))); msg = "Paiement enregistre avec N Paie !"
        conn.commit()
    if request.args.get('edit_paiement'):
        cur.execute("SELECT * FROM paiements WHERE id=?", (request.args.get('edit_paiement'),)); edit_p = cur.fetchone()
    cur.execute("SELECT * FROM etudiants_propres ORDER BY matricule"); etus = cur.fetchall()
    cur.execute("SELECT paiements.*, etudiants_propres.nom as etu_nom FROM paiements LEFT JOIN etudiants_propres ON paiements.matricule=etudiants_propres.matricule ORDER BY paiements.id DESC"); allp = cur.fetchall()
    liste = [r for r in allp if match_q(q, r['matricule'], r['etu_nom'] or "", r['motif'], r['date_paiement'], r['numero_paie'] or "")]
    conn.close()
    opt = "".join(["<option value='"+r['matricule']+"' "+("selected" if edit_p and edit_p['matricule']==r['matricule'] else "")+">"+r['matricule']+" - "+r['nom']+"</option>" for r in etus])
    titre = "Corriger ce Paiement" if edit_p else "Ajouter un Paiement"
    btn = "Sauvegarder la correction" if edit_p else "Enregistrer"
    act = "update" if edit_p else "add"
    hid = "<input type='hidden' name='id' value='"+str(edit_p['id'])+"'>" if edit_p else ""
    tv = edit_p['montant_total'] if edit_p else ""; pv = edit_p['montant_paye'] if edit_p else ""; mv = edit_p['motif'] if edit_p else ""
    lignes = ""
    for r in liste:
        lignes += "<tr><td><b>"+(r['numero_paie'] or "-")+"</b><br>"+r['date_paiement']+"</td><td><b>"+(r['etu_nom'] or "Inconnu")+"</b><br>"+r['matricule']+"</td><td>"+r['motif']+"</td><td>"+str(r['montant_total'])+" $</td><td><b>"+str(r['montant_paye'])+" $</b></td><td><a class='btn-mini edit' href='/admin/paie?edit_paiement="+str(r['id'])+"'>Modifier</a><form method='POST' style='display:inline'><input type='hidden' name='action' value='delete'><input type='hidden' name='id' value='"+str(r['id'])+"'><button class='btn-mini del' style='width:auto'>Supprimer</button></form><a class='btn-mini' style='background:#0D3B8C' href='/paie/"+r['matricule']+"' target='_blank'>Releve</a></td></tr>"
    if not liste:
        lignes = "<tr><td colspan='6' style='text-align:center'>Aucun paiement.</td></tr>"
    total = sum([r['montant_paye'] for r in allp])
    h = STYLE + header('admin') + back_top("/admin") + '<div class="wrap"><div class="box"><h2>Admin - Paie</h2><p>Total encaisse : <b>' + str(total) + ' $</b> | Paiements : <b>' + str(len(allp)) + '</b> | Chaque paiement a un N Paie ex: PAIE/2026/0001</p><div style="background:#EFF6FF;border:2px solid #0D3B8C;border-radius:12px;padding:16px"><h3>' + titre + '</h3><form method="post" enctype="multipart/form-data"><input type="hidden" name="action" value="' + act + '">' + hid + '<select name="matricule">' + opt + '</select><input name="total" type="number" value="' + str(tv) + '" placeholder="Total" required><input name="paye" type="number" value="' + str(pv) + '" placeholder="Paye" required><input name="motif" value="' + str(mv) + '" placeholder="Motif" required><button class="green">' + btn + '</button></form></div><p style="text-align:center;color:green"><b>' + msg + '</b></p><h3>Historique (' + str(len(liste)) + ')</h3>' + search_bar(q, "Rechercher... N Paie, nom, motif...") + '<table><tr><th>N Paie + Date</th><th>Etudiant</th><th>Motif</th><th>Total</th><th>Paye</th><th>Action</th></tr>' + lignes + '</table></div></div>'
    return render_template_string(h)
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        mat = request.form.get('matricule','').strip()
        if mat:
            return redirect("/dashboard/" + mat)
        msg = "Entre ton matricule"
    else:
        msg = ""
    h = STYLE + header('login') + back_top("/") + '<div class="wrap"><div class="box" style="max-width:480px;margin:30px auto;text-align:center">'
    h += '<div style="font-size:50px">🎓</div><h2>Connexion Etudiant</h2><p style="color:#64748B">Entre ton matricule pour voir ta carte, tes notes et ton horaire.</p>'
    if msg: h += '<div class="alert alert-yellow">'+msg+'</div>'
    h += '<form method="post" style="text-align:left"><label>Ton Matricule - ex: UCBC/2025/0001</label><input name="matricule" placeholder="UCBC/2025/0001" required><button class="green">Entrer dans mon Espace &rarr;</button></form>'
    h += '<p style="margin-top:16px"><a href="/">Retour Accueil</a> &nbsp;•&nbsp; <a href="/admin/login">Je suis Admin</a></p></div></div>'
    return render_template_string(h)
@app.route('/notes/<path:mat>')
@app.route('/resultat/<path:mat>')
def voir_resultat(mat):
    conn=get_db(); cur=conn.cursor()
    # --- JURY : on s'assure que les colonnes existent ---
    try: cur.execute("ALTER TABLE notes ADD COLUMN statut TEXT DEFAULT 'brouillon'")
    except: pass
    try: cur.execute("ALTER TABLE notes ADD COLUMN phase TEXT DEFAULT 'normale'")
    except: pass
    try: cur.execute("ALTER TABLE etudiants_propres ADD COLUMN vu_jury TEXT DEFAULT ''")
    except: pass
    conn.commit()
    # L'etudiant vient de voir son resultat -> on marque la phase comme vue
    cur.execute("SELECT statut FROM notes WHERE matricule=? AND statut LIKE 'publie_%' LIMIT 1", (mat,))
    _last = cur.fetchone()
    if _last:
        _phase = _last['statut'].replace('publie_','').replace('_',' ').upper()
        cur.execute("UPDATE etudiants_propres SET vu_jury=? WHERE matricule=?", (_phase, mat))
        conn.commit()
    cur.execute("SELECT * FROM etudiants_propres WHERE matricule=?", (mat,)); e=cur.fetchone()
    if not e:
        conn.close()
        return "Etudiant introuvable : " + mat
    # --- JURY : L'etudiant ne voit QUE ce qui est publie ---
    # On joint avec la table cours pour avoir le vrai nom du cours
    try:
        cur.execute("SELECT notes.note, notes.statut, notes.phase, cours.nom as cours_nom FROM notes LEFT JOIN cours ON cours.id = notes.cours_id WHERE notes.matricule=? AND notes.statut LIKE 'publie_%' ORDER BY cours.nom", (mat,)); notes = cur.fetchall()
    except:
        # Si la jointure echoue (ancienne base), on prend sans jointure
        cur.execute("SELECT note, statut, phase, cours_id FROM notes WHERE matricule=? AND statut LIKE 'publie_%'", (mat,)); notes = cur.fetchall()
    # --- Est-ce qu'il y a des cotes en attente du Jury ? ---
    cur.execute("SELECT COUNT(*) as nb FROM notes WHERE matricule=? AND statut IN ('soumis_jury','valide_jury','brouillon')", (mat,)); en_attente = cur.fetchone()['nb']
    conn.close()
    lignes = ""
    total = 0; nb = 0
    phase_affichee = ""
    for n in notes:
        try:
            cours_nom = n['cours_nom'] if 'cours_nom' in n.keys() and n['cours_nom'] else ("Cours " + str(n['cours_id']) if 'cours_id' in n.keys() else "Cours")
        except:
            cours_nom = "Cours"
        try:
            note_val = n['note']
            phase_affichee = n['phase'] or "normale"
        except:
            note_val = "-"
        # Petite pastille de phase
        coul = {"normale":"#16A34A","recours":"#7C3AED","rattrapage":"#DC2626"}.get(str(phase_affichee).lower(), "#16A34A")
        lignes += "<tr><td><b>"+str(cours_nom)+"</b></td><td><b>"+str(note_val)+" / 20</b></td><td><small style='background:"+coul+";color:white;padding:3px 8px;border-radius:10px'>"+str(phase_affichee).upper()+"</small></td></tr>"
        try: total += float(note_val); nb += 1
        except: pass
    if not lignes:
        if en_attente > 0:
            lignes = "<tr><td colspan='3' style='text-align:center;padding:20px'><b style='color:#92400E'>⏳ En attente de deliberation du Jury</b><br><br>Tes cotes sont chez le Jury. Elles ne sont pas encore publiees.<br>Reviens apres la publication.<br><small>"+str(en_attente)+" cote(s) en attente</small></td></tr>"
        else:
            lignes = "<tr><td colspan='3' style='text-align:center;padding:20px'>Aucune note publiee pour le moment.<br>Reviens apres le Jury.</td></tr>"
    moy = str(round(total/nb, 2)) if nb else "-"
    # Message en haut selon la phase
    if nb > 0:
        banner = '<div style="background:#DCFCE7;border:2px solid #16A34A;border-radius:12px;padding:12px;text-align:center;margin-bottom:12px"><b style="color:#166534">✅ Resultats publies par le Jury : '+str(phase_affichee).upper()+'</b></div>'
    elif en_attente > 0:
        banner = '<div style="background:#FFFBEB;border:2px solid #F59E0B;border-radius:12px;padding:12px;text-align:center;margin-bottom:12px"><b style="color:#92400E">⏳ En deliberation - Jury non publie</b></div>'
    else:
        banner = ''
    h = STYLE + header('resultat') + back_top("/dashboard/"+mat) + '<div class="wrap"><div class="box">'
    h += '<h2>📊 Mon Resultat - '+(e['nom'] or "")+'</h2><p>Matricule : <b>'+mat+'</b> &nbsp;•&nbsp; '+(e['faculte'] or "")+' - '+(e['departement'] or "")+' - '+(e['niveau'] or "")+'</p>'
    h += banner
    h += '<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:16px;padding:16px;text-align:center;margin:16px 0"><span style="font-size:14px;color:#64748B">MOYENNE GENERALE (Cotes publiees seulement)</span><div style="font-size:36px;font-weight:900;color:#0A1931">'+moy+' / 20</div></div>'
    h += '<table><tr><th>Cours / Matiere</th><th>Note / 20</th><th>Phase</th></tr>'+lignes+'</table>'
    h += '<div class="cards" style="margin-top:20px"><a class="card card-navy" href="/dashboard/'+mat+'">⬅ Retour Dashboard</a><a class="card card-gold" href="/carte/'+mat+'">💳 Ma Carte</a></div>'
    h += '</div></div>'
    return render_template_string(h)
# --- ESPACE ENSEIGNANT ---
@app.route('/enseignant/login', methods=['GET','POST'])
def enseignant_login():
    msg = ""
    if request.method == 'POST':
        ident = request.form.get('ident','').strip().lower()
        mdp = request.form.get('mdp','').strip()
        conn = get_db(); cur = conn.cursor()
        ens = None
        try:
            cur.execute("SELECT * FROM enseignants")
            for r in cur.fetchall():
                d = dict(r)
                email = str(d.get('email') or '').strip().lower()
                code = str(d.get('code') or '').strip().lower()
                if email == ident or code == ident:
                    # On recupere le mot de passe, quel que soit son nom de colonne
                    mdp_base = str(d.get('mot_de_passe') or d.get('password') or d.get('mdp') or d.get('pass') or '').strip()
                    # CAS 1 : mot de passe crypte par l'admin (commence par scrypt: ou pbkdf2:)
                    if mdp_base.startswith('scrypt:') or mdp_base.startswith('pbkdf2:'):
                        try:
                            from werkzeug.security import check_password_hash
                            if check_password_hash(mdp_base, mdp):
                                ens = d
                                break
                        except:
                            pass
                    # CAS 2 : mot de passe en clair 1234
                    elif mdp_base == mdp:
                        ens = d
                        break
        except Exception as e:
            msg = f'Erreur base: {e}'
        conn.close()
        if ens:
            session['enseignant'] = ens.get('email') or ident
            return redirect("/enseignant/dashboard")
        else:
            if not msg:
                msg = '<div style="background:#FEE2E2;color:#991B1B;padding:10px;border-radius:10px;margin-bottom:12px">Identifiant ou mot de passe incorrect. Verifie avec l\'administration.</div>'
    h = STYLE + header('enseignant') + back_top("/") + '<div class="wrap"><div class="box" style="max-width:480px;margin:40px auto;text-align:center"><h2>👨‍🏫 Espace Enseignant</h2><p style="color:#64748B">Entre ton email et ton mot de passe</p>' + msg + '<form method="POST"><input name="ident" placeholder="Email - ex: mulendu@gmail.com" required style="width:100%;padding:14px;border:1px solid #E2E8F0;border-radius:10px;margin-bottom:12px"><input name="mdp" type="password" placeholder="Mot de passe - ex: 1234" required style="width:100%;padding:14px;border:1px solid #E2E8F0;border-radius:10px;margin-bottom:12px"><button class="btn btn-gold" style="width:100%">Entrer &rarr;</button></form><br><a href="/">Retour Accueil</a></div></div>'
    return render_template_string(h)

@app.route('/enseignant/dashboard')
def enseignant_dashboard():
    if 'enseignant' not in session and 'enseignant_id' not in session:
        return redirect("/enseignant/login")
    code = session.get('enseignant', f"ID {session.get('enseignant_id')}")
    h = STYLE + header('enseignant') + back_top("/") + '<div class="wrap"><div class="box"><h2>Bonjour Enseignant ' + code + '</h2><p style="color:#64748B">Bienvenue dans ton espace.</p><div class="grille-enseignant"><a class="card card-blue" href="/enseignant/horaire">📚 Mon Horaire<br><small>Voir mon horaire</small></a><a class="card card-green" href="/enseignant/soumissions/2">📥 Soumissions<br><small>Voir les devoirs rendus</small></a><a class="card card-gold" href="/">🏠 Accueil</a></div></div></div>'
    return render_template_string(h)

@app.route('/uploads/<path:filename>')
def uploads(filename):
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    for dos in [os.path.join(base, "uploads"), base, os.path.join(base, "static")]:
        chemin = os.path.join(dos, filename)
        if os.path.exists(chemin):
            return send_file(chemin)
    return "Photo introuvable", 404
# --- HORAIRE ENSEIGNANT : IL VOIT CE QUE L'ADMIN A PUBLIE ---
@app.route('/enseignant/horaire')
def horaire_enseignant():
    # Accepte les 2 types de connexion : avec id OU avec code/gmail
    if 'enseignant' not in session and 'enseignant_id' not in session:
        return redirect("/enseignant/login")

    conn = get_db(); cur = conn.cursor()

    # Cas 1 : tu viens de /dashboard-enseignant/4 -> on a enseignant_id
    if 'enseignant_id' in session:
        cur.execute("SELECT * FROM enseignants WHERE id=?", (session['enseignant_id'],))
        ens = cur.fetchone()
    # Cas 2 : tu viens de /enseignant -> on a enseignant = code/gmail
    else:
        code = session['enseignant']
        cur.execute("SELECT * FROM enseignants WHERE code=? OR gmail=? OR nom=?", (code, code, code))
        ens = cur.fetchone()

    if not ens:
        conn.close()
        return "Enseignant introuvable"

    # CORRIGE : on filtre par l'enseignant, pas par faculte/departement/niveau
    # Et on prend la salle dans cours avec l'alias salle_cours pour ne pas confondre avec horaires.salle (vide)
    cur.execute("""
    SELECT h.*, c.nom as cours_nom, c.prof as prof, c.credits as credits, c.salle as salle_cours
    FROM horaires h
    LEFT JOIN cours c ON c.id = h.cours_id
    WHERE h.enseignant_id=? OR c.prof=?
    ORDER BY h.jour, h.heure_debut
    """, (ens['id'], ens['nom']))
    rows = cur.fetchall(); conn.close()

    lignes = ""
    for r in rows:
        # Nom du cours : priorité à cours_nom qui vient de la table cours
        cours = r['cours_nom'] if r['cours_nom'] else (r['cours'] if 'cours' in r.keys() and r['cours'] else r['cours_id'])
        # Salle : priorité à salle_cours qui vient de la table cours
        salle = r['salle_cours'] if r['salle_cours'] else (r['salle'] if 'salle' in r.keys() and r['salle'] else "Non définie")
        # Heure : supporte heure_debut/heure_fin OU heure
        if 'heure_debut' in r.keys() and r['heure_debut']:
            heure_txt = f"{r['heure_debut']} - {r['heure_fin']}"
        else:
            heure_txt = r['heure'] if 'heure' in r.keys() else ""
        lignes += f"<tr><td>{r['jour']}</td><td>{heure_txt}</td><td>{cours}</td><td><b>{salle}</b></td></tr>"
    if not lignes:
        lignes = "<tr><td colspan='4' style='text-align:center'>Aucun horaire pour le moment.</td></tr>"

    h = STYLE + header('enseignant') + back_top(f"/dashboard-enseignant/{ens['id']}") + f'<div class="wrap">...<div class="box"><h2>Mon Horaire - {ens["nom"]}</h2><table><tr><th>Jour</th><th>Heure</th><th>Cours</th><th>Salle</th></tr>{lignes}</table></div></div>'
    return render_template_string(h)

if __name__ == '__main__':
    import os
    print("=== INTRANET_GRACE V10.4 COMPLET - PHOTO + CARTE ===")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)