"""
Step 49: Seed the health knowledge database with sample documents.
Run once before demo to pre-populate the vector DB.
"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(override=True)

from app.retrieval.store import ingest_text

HEALTH_DOCUMENTS = [
    # ── English Documents ─────────────────────────────────────────────────────
    {
        "title": "Type 2 Diabetes Overview",
        "source": "https://www.mayoclinic.org/diseases-conditions/type-2-diabetes",
        "language": "en",
        "text": """Type 2 diabetes is a chronic condition that affects the way the body metabolizes sugar (glucose).
With type 2 diabetes, the body either doesn't produce enough insulin or it resists insulin.
Symptoms include increased thirst, frequent urination, increased hunger, unintended weight loss, fatigue,
blurred vision, slow-healing sores, and frequent infections.
Risk factors include being overweight, fat distribution in the abdomen, inactivity, family history, race,
prediabetes, gestational diabetes, and polycystic ovary syndrome.
Treatment involves lifestyle changes, blood sugar monitoring, diabetes medications or insulin therapy.
A healthy diet, regular physical activity, and maintaining a healthy weight are the cornerstones of management."""
    },
    {
        "title": "Hypertension (High Blood Pressure)",
        "source": "https://www.who.int/news-room/fact-sheets/detail/hypertension",
        "language": "en",
        "text": """Hypertension, or high blood pressure, is when the force of blood against artery walls is consistently too high.
Normal blood pressure is below 120/80 mmHg. Hypertension is diagnosed at 130/80 mmHg or higher.
It is called the 'silent killer' because most people have no symptoms.
Risk factors include unhealthy diet (high salt), physical inactivity, tobacco and alcohol use, obesity,
family history, stress, and certain chronic conditions.
Complications include heart attack, stroke, kidney disease, and vision loss.
Treatment includes lifestyle changes: reducing salt intake, eating a balanced diet (DASH diet),
regular exercise, limiting alcohol, quitting smoking, and medications such as ACE inhibitors,
beta-blockers, and diuretics."""
    },
    {
        "title": "Asthma: Causes, Symptoms and Treatment",
        "source": "https://www.nhs.uk/conditions/asthma/",
        "language": "en",
        "text": """Asthma is a common long-term condition that affects the airways in the lungs.
The airways become inflamed and can narrow, causing breathing difficulties.
Common symptoms include wheezing, breathlessness, chest tightness, and coughing — especially at night or early morning.
Triggers include allergens (pollen, dust mites, pet dander), respiratory infections, exercise, cold air,
air pollution, smoke, and certain medications like aspirin.
Asthma is managed with inhalers: reliever inhalers (blue — used during an attack) and preventer inhalers
(brown/purple — used daily to reduce inflammation).
Most people with asthma can live normal, active lives with proper management."""
    },
    {
        "title": "Obesity and Weight Management",
        "source": "https://www.cdc.gov/obesity/index.html",
        "language": "en",
        "text": """Obesity is defined as having a Body Mass Index (BMI) of 30 or higher.
It is a complex disease involving excessive amounts of body fat.
Health risks include type 2 diabetes, heart disease, high blood pressure, certain cancers, sleep apnea,
osteoarthritis, and mental health issues.
Causes include genetics, metabolism, environment, behavior, and socioeconomic factors.
Management approaches: healthy eating patterns (reducing calories, increasing vegetables and fruits),
regular physical activity (at least 150 minutes of moderate activity per week), behavioral changes,
prescription medications, and in some cases, bariatric surgery.
Small, sustained changes in diet and activity are more effective than crash diets."""
    },
    {
        "title": "Cardiovascular Disease Prevention",
        "source": "https://www.heart.org/en/health-topics/consumer-healthcare/what-is-cardiovascular-disease",
        "language": "en",
        "text": """Cardiovascular disease (CVD) refers to conditions affecting the heart and blood vessels.
It includes coronary artery disease, heart failure, arrhythmias, and stroke.
Major risk factors: high blood pressure, high cholesterol, smoking, diabetes, obesity,
physical inactivity, unhealthy diet, excessive alcohol, family history, and age.
Prevention strategies: quit smoking, control blood pressure and cholesterol, manage diabetes,
eat a heart-healthy diet (low in saturated fat, sodium, and added sugars),
exercise regularly (at least 150 minutes per week), maintain healthy weight, limit alcohol, manage stress.
Warning signs of heart attack: chest pain or pressure, shortness of breath, pain in arm/shoulder/jaw/back, nausea, cold sweat."""
    },
    {
        "title": "Mental Health: Depression and Anxiety",
        "source": "https://www.who.int/news-room/fact-sheets/detail/depression",
        "language": "en",
        "text": """Depression is a common mental health disorder characterized by persistent sadness,
loss of interest, and inability to carry out daily activities.
Symptoms: persistent low mood, loss of pleasure, sleep disturbances, changes in appetite,
fatigue, difficulty concentrating, feelings of worthlessness, and thoughts of self-harm.
Anxiety disorders involve excessive fear or worry that interferes with daily activities.
Both conditions are treatable. Treatment options include psychotherapy (CBT), medications (antidepressants),
lifestyle changes (regular exercise, adequate sleep, social support), and in severe cases, hospitalization.
Seeking help early leads to better outcomes. Stigma should not prevent people from getting treatment."""
    },
    {
        "title": "Healthy Nutrition Basics",
        "source": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet",
        "language": "en",
        "text": """A healthy diet helps protect against malnutrition and non-communicable diseases.
Key principles: eat plenty of fruits and vegetables (at least 400g/day),
limit free sugars to less than 10% of total energy intake,
reduce saturated fats to less than 10% of total energy intake,
limit salt intake to less than 5g per day,
choose whole grains over refined grains,
include lean proteins: fish, legumes, nuts, and poultry.
Avoid ultra-processed foods, sugary drinks, and trans fats.
Stay hydrated: drink 6-8 glasses of water daily.
Meal planning, reading food labels, and cooking at home are practical ways to improve diet quality."""
    },
    {
        "title": "Exercise and Physical Activity Guidelines",
        "source": "https://www.who.int/news-room/fact-sheets/detail/physical-activity",
        "language": "en",
        "text": """Physical activity is crucial for overall health and disease prevention.
WHO recommendations for adults (18-64 years):
- At least 150-300 minutes of moderate-intensity aerobic activity per week, OR
- 75-150 minutes of vigorous-intensity aerobic activity per week
- Muscle-strengthening activities involving major muscle groups at least 2 days per week.
Benefits: reduces risk of heart disease, stroke, diabetes, cancer, improves mental health,
strengthens bones and muscles, helps maintain healthy weight.
Types of exercise: aerobic (walking, running, swimming, cycling), strength training, flexibility, balance.
Even small amounts of physical activity are better than none. Start slowly and gradually increase."""
    },
    {
        "title": "COVID-19 Symptoms and Prevention",
        "source": "https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html",
        "language": "en",
        "text": """COVID-19 is caused by the SARS-CoV-2 virus. Symptoms appear 2-14 days after exposure.
Common symptoms: fever or chills, cough, shortness of breath, fatigue, muscle aches,
headache, loss of taste or smell, sore throat, congestion, nausea, vomiting, diarrhea.
Prevention: get vaccinated and stay up to date on boosters, wear a well-fitted mask in crowded places,
improve ventilation, wash hands frequently, avoid close contact with sick people,
cover coughs and sneezes, clean and disinfect frequently touched surfaces.
Seek emergency care if you experience: trouble breathing, persistent chest pain, confusion,
inability to wake or stay awake, or pale/gray/blue-colored skin or lips."""
    },
    {
        "title": "Sleep Health and Sleep Disorders",
        "source": "https://www.cdc.gov/sleep/index.html",
        "language": "en",
        "text": """Sleep is essential for physical and mental health. Adults need 7-9 hours of sleep per night.
Sleep deprivation increases risk of obesity, heart disease, diabetes, depression, and impaired immune function.
Common sleep disorders: insomnia (difficulty falling/staying asleep), sleep apnea (breathing interruptions),
restless leg syndrome, and narcolepsy.
Sleep hygiene tips: maintain a consistent sleep schedule, create a restful environment (dark, quiet, cool),
avoid screens 1 hour before bed, limit caffeine after noon, avoid large meals before sleep,
exercise regularly but not close to bedtime, manage stress through relaxation techniques."""
    },

    # ── Arabic Documents ──────────────────────────────────────────────────────
    {
        "title": "السكري من النوع الثاني",
        "source": "https://www.mayoclinic.org/ar/diseases-conditions/type-2-diabetes",
        "language": "ar",
        "text": """مرض السكري من النوع الثاني هو حالة مزمنة تؤثر على الطريقة التي يستقلب بها الجسم السكر.
الأعراض تشمل: كثرة التبول، العطش الشديد، الجوع المتزايد، فقدان الوزن غير المبرر، التعب،
ضبابية الرؤية، بطء التئام الجروح، والتعرض المتكرر للعدوى.
عوامل الخطر: زيادة الوزن، قلة النشاط البدني، التاريخ العائلي، وارتفاع ضغط الدم.
العلاج يشمل: تغيير نمط الحياة، مراقبة نسبة السكر في الدم، الأدوية الفموية مثل الميتفورمين،
وفي بعض الحالات الأنسولين.
الوقاية: الحفاظ على وزن صحي، ممارسة الرياضة بانتظام، وتناول غذاء متوازن."""
    },
    {
        "title": "ارتفاع ضغط الدم",
        "source": "https://www.who.int/ar/news-room/fact-sheets/detail/hypertension",
        "language": "ar",
        "text": """ارتفاع ضغط الدم يحدث عندما تكون قوة ضخ الدم على جدران الشرايين مرتفعة باستمرار.
يُعرف بـ"القاتل الصامت" لأن معظم المصابين لا تظهر عليهم أعراض.
القراءة الطبيعية: أقل من 120/80 ملم زئبق. التشخيص عند 130/80 أو أعلى.
المضاعفات تشمل: النوبة القلبية، السكتة الدماغية، الفشل الكلوي، وتلف الرؤية.
العلاج يشمل: تقليل الملح في الطعام، ممارسة الرياضة، الإقلاع عن التدخين، تقليل الكحول،
والأدوية مثل مثبطات الإنزيم المحول للأنجيوتنسين وحاصرات بيتا."""
    },
    {
        "title": "التغذية الصحية",
        "source": "https://www.who.int/ar/news-room/fact-sheets/detail/healthy-diet",
        "language": "ar",
        "text": """النظام الغذائي الصحي يحمي من سوء التغذية والأمراض غير المعدية.
المبادئ الأساسية: تناول كميات وفيرة من الفواكه والخضروات (400 غرام على الأقل يومياً)،
تقليل السكريات الحرة إلى أقل من 10% من إجمالي الطاقة،
تقليل الدهون المشبعة، الحد من الملح إلى أقل من 5 غرامات يومياً،
اختيار الحبوب الكاملة بدلاً من المكررة، تضمين البروتينات الخالية من الدهون.
تجنب الأطعمة فائقة المعالجة والمشروبات السكرية.
اشرب 6-8 أكواب من الماء يومياً للحفاظ على الترطيب."""
    },
    {
        "title": "صحة القلب والوقاية من أمراضه",
        "source": "https://www.who.int/ar/health-topics/cardiovascular-diseases",
        "language": "ar",
        "text": """أمراض القلب والأوعية الدموية هي السبب الرئيسي للوفاة عالمياً.
عوامل الخطر: ارتفاع ضغط الدم، ارتفاع الكوليسترول، التدخين، السكري، السمنة، وقلة النشاط البدني.
أعراض النوبة القلبية: ألم أو ضغط في الصدر، ضيق في التنفس، ألم في الذراع أو الكتف أو الفك،
غثيان، تعرق بارد.
الوقاية: الإقلاع عن التدخين، التحكم في ضغط الدم والكوليسترول، إدارة مرض السكري،
تناول غذاء صحي للقلب، ممارسة الرياضة بانتظام، والحفاظ على وزن صحي."""
    },
    {
        "title": "الصحة النفسية والاكتئاب",
        "source": "https://www.who.int/ar/news-room/fact-sheets/detail/depression",
        "language": "ar",
        "text": """الاكتئاب من أكثر الاضطرابات النفسية شيوعاً في العالم ويصيب أكثر من 280 مليون شخص.
الأعراض: الحزن المستمر، فقدان الاهتمام بالأنشطة المعتادة، اضطرابات النوم، تغيرات في الشهية،
التعب، صعوبة التركيز، والأفكار السلبية.
قلق القلق يتمثل في الخوف أو التوتر المفرط الذي يتعارض مع الحياة اليومية.
العلاج: العلاج النفسي (العلاج المعرفي السلوكي)، الأدوية المضادة للاكتئاب،
تغيير نمط الحياة (الرياضة، النوم الكافي، الدعم الاجتماعي).
لا تتردد في طلب المساعدة — الصحة النفسية بقدر أهمية الصحة الجسدية."""
    },
    {
        "title": "السمنة وإدارة الوزن",
        "source": "https://www.who.int/ar/news-room/fact-sheets/detail/obesity-and-overweight",
        "language": "ar",
        "text": """السمنة تُعرَّف بمؤشر كتلة الجسم 30 أو أعلى.
مخاطرها الصحية: السكري من النوع الثاني، أمراض القلب، ارتفاع ضغط الدم، بعض أنواع السرطان،
توقف التنفس أثناء النوم، وآلام المفاصل.
أسباب السمنة: الجينات، النظام الغذائي غير الصحي، قلة النشاط البدني، والعوامل البيئية.
طرق الإدارة: اتباع نظام غذائي صحي بسعرات حرارية منخفضة، ممارسة 150 دقيقة على الأقل من النشاط
البدني أسبوعياً، تعديل السلوك، وفي الحالات الشديدة الأدوية أو الجراحة.
التغييرات الصغيرة والمستدامة أكثر فاعلية من الحميات القاسية."""
    },
]

def seed():
    print(f"Seeding database with {len(HEALTH_DOCUMENTS)} health documents...")
    print("This may take a few minutes (embedding each document).\n")

    total_chunks = 0
    for i, doc in enumerate(HEALTH_DOCUMENTS):
        print(f"[{i+1}/{len(HEALTH_DOCUMENTS)}] Ingesting: {doc['title']}")
        ids = ingest_text(
            text=doc["text"],
            title=doc["title"],
            source=doc["source"],
        )
        total_chunks += len(ids)

    print(f"\nDone! Inserted {total_chunks} chunks from {len(HEALTH_DOCUMENTS)} documents.")
    print("Your health knowledge base is ready.")

if __name__ == "__main__":
    seed()
