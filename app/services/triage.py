"""
Emergency Triage service.
A guided decision-tree that asks yes/no questions,
determines severity, and tells the user exactly what to do.
No Claude API needed — deterministic logic only.
"""

# ── Decision tree ─────────────────────────────────────────────────────────────
# Each node: {"q_en": ..., "q_ar": ..., "yes": node_id, "no": node_id}
# Terminal node: {"level": "emergency"|"urgent"|"soon"|"home", "advice_en": ..., "advice_ar": ...}

TREE: dict = {
    # ── Root ──────────────────────────────────────────────────────────────────
    "start": {
        "q_en": "Are you experiencing chest pain, pressure, or tightness?",
        "q_ar": "هل تعاني من ألم في الصدر أو ضغط أو شعور بالضيق؟",
        "yes": "chest_yes",
        "no":  "breathing",
    },

    # ── Chest pain branch ─────────────────────────────────────────────────────
    "chest_yes": {
        "q_en": "Does the pain spread to your arm, jaw, or back?",
        "q_ar": "هل ينتشر الألم إلى ذراعك أو فكك أو ظهرك؟",
        "yes": "EMERGENCY_HEART",
        "no":  "chest_breathless",
    },
    "chest_breathless": {
        "q_en": "Are you also short of breath or sweating heavily?",
        "q_ar": "هل تعاني أيضاً من ضيق التنفس أو التعرق الشديد؟",
        "yes": "EMERGENCY_HEART",
        "no":  "URGENT_CHEST",
    },

    # ── Breathing branch ──────────────────────────────────────────────────────
    "breathing": {
        "q_en": "Are you having severe difficulty breathing right now?",
        "q_ar": "هل تعاني من صعوبة شديدة في التنفس الآن؟",
        "yes": "EMERGENCY_BREATHING",
        "no":  "consciousness",
    },

    # ── Consciousness branch ──────────────────────────────────────────────────
    "consciousness": {
        "q_en": "Has someone nearby lost consciousness or are they unresponsive?",
        "q_ar": "هل فقد شخص قريب منك وعيه أو أنه لا يستجيب؟",
        "yes": "EMERGENCY_UNRESPONSIVE",
        "no":  "bleeding",
    },

    # ── Bleeding branch ───────────────────────────────────────────────────────
    "bleeding": {
        "q_en": "Is there severe uncontrolled bleeding (won't stop after 10 min of pressure)?",
        "q_ar": "هل هناك نزيف شديد لا يمكن السيطرة عليه (لا يتوقف بعد 10 دقائق من الضغط)؟",
        "yes": "EMERGENCY_BLEEDING",
        "no":  "stroke",
    },

    # ── Stroke signs branch ───────────────────────────────────────────────────
    "stroke": {
        "q_en": "Is anyone showing sudden face drooping, arm weakness, or speech difficulty?",
        "q_ar": "هل يظهر على أحدهم فجأة تدلي الوجه أو ضعف الذراع أو صعوبة في الكلام؟",
        "yes": "EMERGENCY_STROKE",
        "no":  "high_fever",
    },

    # ── High fever branch ─────────────────────────────────────────────────────
    "high_fever": {
        "q_en": "Do you have a fever above 39.5°C (103°F)?",
        "q_ar": "هل لديك حمى أعلى من 39.5°C (103°F)؟",
        "yes": "fever_child",
        "no":  "injury",
    },
    "fever_child": {
        "q_en": "Is it a child under 3 months old OR is the fever accompanied by a stiff neck or rash?",
        "q_ar": "هل هو طفل دون 3 أشهر أو هل الحمى مصحوبة بتيبس الرقبة أو طفح جلدي؟",
        "yes": "EMERGENCY_FEVER",
        "no":  "URGENT_FEVER",
    },

    # ── Injury branch ─────────────────────────────────────────────────────────
    "injury": {
        "q_en": "Have you had a fall, accident, or head injury recently?",
        "q_ar": "هل تعرضت لسقوط أو حادث أو إصابة في الرأس مؤخراً؟",
        "yes": "injury_severe",
        "no":  "pain_severe",
    },
    "injury_severe": {
        "q_en": "Is there severe pain, visible deformity (like a broken bone), or loss of feeling?",
        "q_ar": "هل هناك ألم شديد أو تشوه واضح (مثل كسر عظمة) أو فقدان الإحساس؟",
        "yes": "URGENT_INJURY",
        "no":  "SOON_INJURY",
    },

    # ── Severe pain branch ────────────────────────────────────────────────────
    "pain_severe": {
        "q_en": "Are you in severe pain (7 or more out of 10)?",
        "q_ar": "هل تعاني من ألم شديد (7 أو أكثر من 10)؟",
        "yes": "pain_location",
        "no":  "symptoms_mild",
    },
    "pain_location": {
        "q_en": "Is the pain in your abdomen and has it been getting worse for more than 6 hours?",
        "q_ar": "هل الألم في البطن وتفاقم منذ أكثر من 6 ساعات؟",
        "yes": "URGENT_ABDO",
        "no":  "URGENT_PAIN",
    },

    # ── Mild symptoms branch ──────────────────────────────────────────────────
    "symptoms_mild": {
        "q_en": "Do you have symptoms like headache, cough, sore throat, or mild stomach upset?",
        "q_ar": "هل لديك أعراض مثل صداع أو سعال أو التهاب الحلق أو اضطراب معدي خفيف؟",
        "yes": "SOON_MILD",
        "no":  "HOME_WELL",
    },

    # ── TERMINAL NODES ────────────────────────────────────────────────────────
    "EMERGENCY_HEART": {
        "level": "emergency",
        "advice_en": (
            "🚨 **Call emergency services (911/999) immediately.**\n\n"
            "These symptoms may indicate a **heart attack**. Do not drive yourself.\n\n"
            "While waiting:\n"
            "- Sit or lie down in a comfortable position\n"
            "- Loosen tight clothing\n"
            "- If advised by a doctor and not allergic, chew one aspirin (300 mg)\n"
            "- Stay calm and keep someone with you"
        ),
        "advice_ar": (
            "🚨 **اتصل بخدمات الطوارئ (911/999) فوراً.**\n\n"
            "قد تشير هذه الأعراض إلى **نوبة قلبية**. لا تقود السيارة بنفسك.\n\n"
            "أثناء الانتظار:\n"
            "- اجلس أو استلقِ في وضع مريح\n"
            "- أرخِ الملابس الضيقة\n"
            "- إذا أوصى طبيب ولم تكن مصاباً بحساسية، امضغ أسبرين (300 مغ)\n"
            "- ابقَ هادئاً واجعل شخصاً ما بجانبك"
        ),
    },
    "EMERGENCY_BREATHING": {
        "level": "emergency",
        "advice_en": (
            "🚨 **Call emergency services (911/999) immediately.**\n\n"
            "Severe difficulty breathing is a **life-threatening emergency**.\n\n"
            "While waiting:\n"
            "- Sit upright — do not lie flat\n"
            "- Use an inhaler if you have one (asthma/COPD)\n"
            "- Loosen any tight clothing around neck and chest\n"
            "- Keep calm and breathe slowly"
        ),
        "advice_ar": (
            "🚨 **اتصل بخدمات الطوارئ (911/999) فوراً.**\n\n"
            "صعوبة التنفس الشديدة **حالة طارئة تهدد الحياة**.\n\n"
            "أثناء الانتظار:\n"
            "- اجلس في وضع مستقيم — لا تستلقِ على الأرض\n"
            "- استخدم جهاز الاستنشاق إذا كان لديك واحد (للربو/الانسداد الرئوي)\n"
            "- أرخِ أي ملابس ضيقة حول الرقبة والصدر\n"
            "- حافظ على هدوئك وتنفس ببطء"
        ),
    },
    "EMERGENCY_UNRESPONSIVE": {
        "level": "emergency",
        "advice_en": (
            "🚨 **Call emergency services (911/999) immediately.**\n\n"
            "An unresponsive person may need **CPR**.\n\n"
            "While waiting:\n"
            "- Check for breathing (look, listen, feel)\n"
            "- If not breathing, begin CPR: 30 chest compressions, then 2 rescue breaths\n"
            "- Use an AED if available nearby\n"
            "- Stay on the phone with the dispatcher"
        ),
        "advice_ar": (
            "🚨 **اتصل بخدمات الطوارئ (911/999) فوراً.**\n\n"
            "قد يحتاج الشخص غير المستجيب إلى **الإنعاش القلبي الرئوي (CPR)**.\n\n"
            "أثناء الانتظار:\n"
            "- تحقق من التنفس (انظر، استمع، أحس)\n"
            "- إذا لم يكن يتنفس، ابدأ CPR: 30 ضغطة على الصدر ثم نفسين إنقاذ\n"
            "- استخدم جهاز AED إذا كان متاحاً بالقرب\n"
            "- ابقَ على الهاتف مع المسعف"
        ),
    },
    "EMERGENCY_BLEEDING": {
        "level": "emergency",
        "advice_en": (
            "🚨 **Call emergency services (911/999) immediately.**\n\n"
            "Severe uncontrolled bleeding can be fatal within minutes.\n\n"
            "While waiting:\n"
            "- Apply firm, continuous pressure with a clean cloth\n"
            "- Do not remove the cloth — add more on top if it soaks through\n"
            "- Elevate the injured limb above heart level if possible\n"
            "- Keep the person warm and still"
        ),
        "advice_ar": (
            "🚨 **اتصل بخدمات الطوارئ (911/999) فوراً.**\n\n"
            "النزيف الشديد غير المنضبط يمكن أن يكون قاتلاً في غضون دقائق.\n\n"
            "أثناء الانتظار:\n"
            "- اضغط بثبات ومستمر بقماش نظيف\n"
            "- لا تزيل القماش — أضف المزيد فوقه إذا نقع بالدم\n"
            "- ارفع الطرف المصاب فوق مستوى القلب إذا أمكن\n"
            "- أبقِ الشخص دافئاً وثابتاً"
        ),
    },
    "EMERGENCY_STROKE": {
        "level": "emergency",
        "advice_en": (
            "🚨 **Call emergency services (911/999) immediately — use the FAST test.**\n\n"
            "**F**ace drooping · **A**rm weakness · **S**peech difficulty · **T**ime to call\n\n"
            "Every minute counts with a stroke.\n\n"
            "While waiting:\n"
            "- Note the exact time symptoms started\n"
            "- Do not give the person food, water, or medication\n"
            "- Keep them calm and still\n"
            "- Do not let them drive themselves"
        ),
        "advice_ar": (
            "🚨 **اتصل بخدمات الطوارئ (911/999) فوراً — استخدم اختبار FAST.**\n\n"
            "**F** تدلي الوجه · **A** ضعف الذراع · **S** صعوبة الكلام · **T** وقت الاتصال\n\n"
            "كل دقيقة تهم في حالة السكتة الدماغية.\n\n"
            "أثناء الانتظار:\n"
            "- سجّل الوقت الدقيق الذي بدأت فيه الأعراض\n"
            "- لا تعطِ الشخص طعاماً أو ماءً أو دواءً\n"
            "- أبقِه هادئاً وثابتاً\n"
            "- لا تدعه يقود السيارة بنفسه"
        ),
    },
    "EMERGENCY_FEVER": {
        "level": "emergency",
        "advice_en": (
            "🚨 **Go to the emergency room immediately.**\n\n"
            "A very high fever in a newborn or with stiff neck/rash may indicate **meningitis** or **sepsis**.\n\n"
            "While heading to the ER:\n"
            "- Do not wait for symptoms to worsen\n"
            "- Keep the child or person cool with a damp cloth\n"
            "- Do not overdress them"
        ),
        "advice_ar": (
            "🚨 **اذهب إلى غرفة الطوارئ فوراً.**\n\n"
            "الحمى الشديدة جداً عند الرضع أو المصحوبة بتيبس الرقبة/طفح جلدي قد تشير إلى **التهاب السحايا** أو **الإنتان**.\n\n"
            "أثناء التوجه إلى الطوارئ:\n"
            "- لا تنتظر تفاقم الأعراض\n"
            "- أبرِد الطفل أو الشخص بقطعة قماش مبللة\n"
            "- لا تلبسه ملابس ثقيلة"
        ),
    },
    "URGENT_CHEST": {
        "level": "urgent",
        "advice_en": (
            "⚠️ **Go to an urgent care clinic or emergency room within 1-2 hours.**\n\n"
            "Chest pain without spreading symptoms still needs prompt evaluation to rule out serious causes.\n\n"
            "- If pain worsens or new symptoms appear (sweating, spreading pain, breathlessness), call 911 immediately\n"
            "- Avoid strenuous activity until evaluated"
        ),
        "advice_ar": (
            "⚠️ **اذهب إلى عيادة طوارئ أو طوارئ المستشفى خلال 1-2 ساعة.**\n\n"
            "ألم الصدر دون أعراض انتشار لا يزال يحتاج إلى تقييم سريع لاستبعاد الأسباب الخطيرة.\n\n"
            "- إذا تفاقم الألم أو ظهرت أعراض جديدة (تعرق، ألم منتشر، ضيق تنفس)، اتصل بالطوارئ فوراً\n"
            "- تجنب المجهود الشديد حتى يتم التقييم"
        ),
    },
    "URGENT_FEVER": {
        "level": "urgent",
        "advice_en": (
            "⚠️ **See a doctor today (urgent care or GP) within a few hours.**\n\n"
            "A high fever needs medical evaluation, especially if it has lasted more than 2 days.\n\n"
            "- Take paracetamol or ibuprofen to bring down the fever\n"
            "- Stay well hydrated\n"
            "- Watch for any stiff neck, rash, or confusion — if these appear, go to the ER immediately"
        ),
        "advice_ar": (
            "⚠️ **قم بزيارة طبيب اليوم (رعاية عاجلة أو طبيب عام) خلال ساعات قليلة.**\n\n"
            "الحمى الشديدة تحتاج إلى تقييم طبي، خاصة إذا استمرت لأكثر من يومين.\n\n"
            "- تناول باراسيتامول أو إيبوبروفين لخفض الحمى\n"
            "- حافظ على الترطيب الجيد\n"
            "- راقب أي تيبس في الرقبة أو طفح جلدي أو ارتباك — إذا ظهرت، اذهب للطوارئ فوراً"
        ),
    },
    "URGENT_INJURY": {
        "level": "urgent",
        "advice_en": (
            "⚠️ **Go to urgent care or an emergency room now.**\n\n"
            "Possible fracture or serious injury needs X-ray and medical assessment.\n\n"
            "- Do not move a potentially fractured limb unnecessarily\n"
            "- Apply ice wrapped in cloth (not directly) to reduce swelling\n"
            "- If you cannot bear weight at all, use a wheelchair or stretcher"
        ),
        "advice_ar": (
            "⚠️ **اذهب إلى الرعاية العاجلة أو طوارئ المستشفى الآن.**\n\n"
            "كسر محتمل أو إصابة خطيرة تحتاج إلى أشعة سينية وتقييم طبي.\n\n"
            "- لا تحرك الطرف المكسور المحتمل دون ضرورة\n"
            "- ضع ثلجاً ملفوفاً بقماش (ليس مباشرة) لتقليل التورم\n"
            "- إذا كنت لا تستطيع تحمل الوزن نهائياً، استخدم كرسي متحرك أو نقالة"
        ),
    },
    "URGENT_ABDO": {
        "level": "urgent",
        "advice_en": (
            "⚠️ **Go to urgent care or an emergency room within 1-2 hours.**\n\n"
            "Worsening abdominal pain over 6+ hours could indicate appendicitis, kidney stones, or other serious causes.\n\n"
            "- Do not eat or drink anything until evaluated (in case surgery is needed)\n"
            "- Note if pain moves location (e.g., to lower right — possible appendix)\n"
            "- If fever develops or pain becomes unbearable, call 911 immediately"
        ),
        "advice_ar": (
            "⚠️ **اذهب إلى الرعاية العاجلة أو طوارئ المستشفى خلال 1-2 ساعة.**\n\n"
            "ألم البطن المتفاقم على مدى 6+ ساعات قد يشير إلى التهاب الزائدة أو حصوات الكلى أو أسباب خطيرة أخرى.\n\n"
            "- لا تأكل أو تشرب شيئاً حتى يتم التقييم (في حالة الحاجة لجراحة)\n"
            "- لاحظ ما إذا كان الألم ينتقل (مثل إلى أسفل اليمين — احتمال التهاب الزائدة)\n"
            "- إذا ظهرت حمى أو أصبح الألم لا يحتمل، اتصل بالطوارئ فوراً"
        ),
    },
    "URGENT_PAIN": {
        "level": "urgent",
        "advice_en": (
            "⚠️ **Contact your doctor or visit urgent care today.**\n\n"
            "Severe pain (7+/10) needs same-day evaluation to identify the cause and provide relief.\n\n"
            "- Over-the-counter pain relief (ibuprofen, paracetamol) may help temporarily\n"
            "- If pain suddenly spikes to 10/10 or you feel very unwell, go to the ER"
        ),
        "advice_ar": (
            "⚠️ **تواصل مع طبيبك أو قم بزيارة الرعاية العاجلة اليوم.**\n\n"
            "الألم الشديد (7+/10) يحتاج إلى تقييم في نفس اليوم لتحديد السبب وتخفيف الألم.\n\n"
            "- مسكنات الألم التي لا تستلزم وصفة طبية (إيبوبروفين، باراسيتامول) قد تساعد مؤقتاً\n"
            "- إذا ارتفع الألم فجأة إلى 10/10 أو شعرت بتوعك شديد، اذهب للطوارئ"
        ),
    },
    "SOON_INJURY": {
        "level": "soon",
        "advice_en": (
            "📅 **Book a GP or clinic appointment within 1-2 days.**\n\n"
            "Your injury doesn't appear immediately serious but should still be checked.\n\n"
            "- Rest and avoid putting stress on the injured area\n"
            "- Apply ice (wrapped) for 20 minutes every 2 hours for the first 48 hours\n"
            "- If swelling increases significantly or pain worsens, go to urgent care sooner"
        ),
        "advice_ar": (
            "📅 **احجز موعداً مع طبيب عام أو عيادة خلال 1-2 يومين.**\n\n"
            "إصابتك لا تبدو خطيرة فوراً لكن يجب فحصها.\n\n"
            "- استرح وتجنب وضع ضغط على المنطقة المصابة\n"
            "- ضع ثلجاً (ملفوفاً) لمدة 20 دقيقة كل ساعتين خلال أول 48 ساعة\n"
            "- إذا ازداد التورم بشكل ملحوظ أو تفاقم الألم، اذهب للرعاية العاجلة في وقت أبكر"
        ),
    },
    "SOON_MILD": {
        "level": "soon",
        "advice_en": (
            "📅 **Schedule a GP appointment within 2-3 days or call your doctor's office.**\n\n"
            "Your symptoms suggest a common illness (cold, mild infection, etc.) that needs monitoring.\n\n"
            "- Rest well and stay hydrated\n"
            "- Paracetamol or ibuprofen for fever/pain as needed\n"
            "- Over-the-counter remedies can help with symptoms\n"
            "- Return here if symptoms worsen significantly"
        ),
        "advice_ar": (
            "📅 **احجز موعداً مع طبيب عام خلال 2-3 أيام أو اتصل بعيادة طبيبك.**\n\n"
            "تشير أعراضك إلى مرض شائع (برد، عدوى خفيفة، إلخ) يحتاج إلى متابعة.\n\n"
            "- استرح جيداً وحافظ على الترطيب\n"
            "- باراسيتامول أو إيبوبروفين للحمى/الألم حسب الحاجة\n"
            "- العلاجات التي لا تستلزم وصفة طبية تساعد في تخفيف الأعراض\n"
            "- عد إلى هنا إذا تفاقمت الأعراض بشكل ملحوظ"
        ),
    },
    "HOME_WELL": {
        "level": "home",
        "advice_en": (
            "✅ **Your answers don't indicate an emergency. You can manage at home for now.**\n\n"
            "General wellness tips:\n"
            "- Stay hydrated and get adequate rest\n"
            "- Maintain a balanced diet and light activity\n"
            "- Monitor any new or worsening symptoms\n\n"
            "If you develop any concerning symptoms in the future, run this triage again.\n"
            "For general health questions, visit the **Health Q&A** service."
        ),
        "advice_ar": (
            "✅ **إجاباتك لا تشير إلى حالة طارئة. يمكنك المتابعة في المنزل الآن.**\n\n"
            "نصائح للصحة العامة:\n"
            "- حافظ على الترطيب والراحة الكافية\n"
            "- اتبع نظاماً غذائياً متوازناً ونشاطاً خفيفاً\n"
            "- راقب أي أعراض جديدة أو متفاقمة\n\n"
            "إذا ظهرت أعراض مقلقة في المستقبل، أعد تشغيل هذا الفرز.\n"
            "للأسئلة الصحية العامة، قم بزيارة خدمة **الأسئلة الصحية**."
        ),
    },
}

# ── Severity metadata ─────────────────────────────────────────────────────────
SEVERITY_META = {
    "emergency": {
        "label_en":  "EMERGENCY",
        "label_ar":  "طوارئ",
        "color":     "#ef4444",
        "bg":        "#fef2f2",
        "border":    "#fca5a5",
        "icon":      "🚨",
    },
    "urgent": {
        "label_en":  "URGENT",
        "label_ar":  "عاجل",
        "color":     "#f59e0b",
        "bg":        "#fffbeb",
        "border":    "#fcd34d",
        "icon":      "⚠️",
    },
    "soon": {
        "label_en":  "SEE A DOCTOR SOON",
        "label_ar":  "راجع طبيباً قريباً",
        "color":     "#3b82f6",
        "bg":        "#eff6ff",
        "border":    "#93c5fd",
        "icon":      "📅",
    },
    "home": {
        "label_en":  "MANAGE AT HOME",
        "label_ar":  "إدارة في المنزل",
        "color":     "#22c55e",
        "bg":        "#f0fdf4",
        "border":    "#86efac",
        "icon":      "✅",
    },
}


def is_terminal(node_id: str) -> bool:
    """Returns True if the node is a leaf (result) node, not a question node."""
    node = TREE.get(node_id, {})
    return "level" in node


def get_node(node_id: str) -> dict:
    return TREE.get(node_id, {})


def get_question(node_id: str, language: str) -> str:
    node = TREE.get(node_id, {})
    return node.get("q_ar" if language == "ar" else "q_en", "")


def get_next(node_id: str, answer_yes: bool) -> str:
    node = TREE.get(node_id, {})
    return node.get("yes" if answer_yes else "no", "HOME_WELL")


def get_result(node_id: str, language: str) -> dict:
    """Returns the terminal node result with advice in the requested language."""
    node = TREE.get(node_id, {})
    level = node.get("level", "home")
    advice = node.get("advice_ar" if language == "ar" else "advice_en", "")
    meta = SEVERITY_META[level]
    return {
        "level": level,
        "label": meta["label_ar"] if language == "ar" else meta["label_en"],
        "advice": advice,
        "color": meta["color"],
        "bg": meta["bg"],
        "border": meta["border"],
        "icon": meta["icon"],
    }