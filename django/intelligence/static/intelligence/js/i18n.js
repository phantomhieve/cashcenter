/**
 * CashCenter Market Intelligence — Bilingual Internationalization Engine (English / हिन्दी)
 *
 * Dedicated strictly to the Market Intelligence application.
 * Seamlessly manages dual datasets (EN & HI) with zero runtime latency,
 * complete UI translation coverage, and localStorage persistence.
 */
(function (window, document) {
    'use strict';

    var STORAGE_KEY = 'cashcenter_intel_lang';

    // Comprehensive English to Hindi translation dictionary
    var DICTIONARY = {
        // Navigation & Brand
        "Business Insights": "व्यापारिक अंतर्दृष्टि (एआई)",
        "AI": "एआई",
        "Shop Ledger": "दुकान बहीखाता",
        "Lock": "सुरक्षित लॉक",
        "Return to Legacy Shop Ledger": "पुराने दुकान बहीखाते पर लौटें",
        "Lock Intelligence Dashboard": "इंटेलिजेंस डैशबोर्ड लॉक करें",
        "CashCenter Insights • Powered by Google Gemini": "कैशसेंटर इंटेलिजेंस • गूगल जेमिनी द्वारा संचालित",
        "CashCenter Insights \u2022 Powered by Google Gemini": "कैशसेंटर इंटेलिजेंस • गूगल जेमिनी द्वारा संचालित",
        "Advice refreshes once every 30 days • Based on your own ledger and live market prices": "सुझाव हर 30 दिन में एक बार अपडेट होते हैं • आपके बहीखाते और मौजूदा थोक भावों पर आधारित",
        "Advice refreshes once every 30 days \u2022 Based on your own ledger and live market prices": "सुझाव हर 30 दिन में एक बार अपडेट होते हैं • आपके बहीखाते और मौजूदा थोक भावों पर आधारित",

        // Eyebrows & Greetings
        "Good morning": "सुप्रभात",
        "Good afternoon": "शुभ दोपहर",
        "Good evening": "शुभ संध्या",
        "Welcome back": "स्वागत है",
        "Bara Bazar, Darbhanga, Bihar": "बड़ा बाजार, दरभंगा, बिहार",
        "Turnaround Intelligence": "व्यापारिक अंतर्दृष्टि (एआई)",
        "Refreshed": "अंतिम अपडेट",
        "Ready to refresh": "अपडेट के लिए तैयार",
        "Next refresh in": "अगला अपडेट",
        "Next refresh opens on": "अगला रिफ्रेश उपलब्ध होगा:",
        "days to go": "दिन शेष",
        "Current": "वर्तमान",
        "All numbers here match your transport ledger for": "सभी आंकड़े आपके ट्रांसपोर्ट बहीखाते से सत्यापित हैं:",
        "No ledger entries recorded yet. Add bills in the Shop Ledger to see live numbers.": "अभी तक कोई प्रविष्टि नहीं मिली है। लाइव आंकड़े देखने के लिए बहीखाते में बिल जोड़ें।",

        // Section Nav
        "Overview": "एक नज़र में",
        "At a glance": "एक नज़र में",
        "What to watch": "सतर्कता बिंदु",
        "Your numbers": "वित्तीय आंकड़े",
        "90-day plan": "90-दिवसीय कार्ययोजना",
        "Full analysis": "विस्तृत विश्लेषण",
        "The full analysis": "विस्तृत विश्लेषण",
        "Market prices": "बाजार थोक भाव",
        "History": "पिछले विश्लेषण",
        "Past refreshes": "पिछले विश्लेषण",

        // Hero Card
        "The big picture": "मुख्य सार (The Big Picture)",
        "Do this first": "प्राथमिक कार्य (Do This First)",
        "Confidence: High": "विश्वसनीयता: उच्च",
        "Confidence: Moderate": "विश्वसनीयता: मध्यम",
        "Confidence: Low": "विश्वसनीयता: कम",
        "AI Business Assessment": "एआई व्यापार मूल्यांकन",
        "Grounding confidence": "डेटा सत्यापन विश्वसनीयता",
        "High": "उच्च",
        "Moderate": "मध्यम",
        "Low": "कम",
        "No hallucination detected": "तथ्यों की पूर्ण पुष्टि (कोई विसंगति नहीं)",
        "Hallucination check passed": "तथ्य सत्यापन सफल",
        "Direct advice tied directly to your bills": "आपके वास्तविक बिलों और बहीखाते पर आधारित सलाह",
        "Immediate focus — what to do first": "प्राथमिक कार्य — सबसे पहले क्या करें:",

        // KPI Cards
        "Goods bought": "खरीदा गया माल",
        "Freight paid": "चुकाया गया भाड़ा",
        "Still on the road": "रास्ते में (ट्रांजिट)",
        "Average delivery time": "औसत डिलीवरी समय",
        "Suppliers": "सप्लायर्स (आपूर्तिकर्ता)",
        "Bales received": "प्राप्त गांठें (बेल्स)",

        // KPI Hints
        "Total value of supplier bills recorded in your ledger this year.": "इस वर्ष आपके बहीखाते में दर्ज सप्लायर बिलों का कुल मूल्य।",
        "Transport cost added on top of goods. Under ~5% is healthy for this trade.": "माल की लागत पर लगा भाड़ा। थोक वस्त्र व्यापार में 5% से कम भाड़ा स्वस्थ माना जाता है।",
        "Consignments with a bill but no delivery date yet. Your money is tied up until they arrive.": "वे चालान जिनका बिल बन चुका है पर डिलीवरी अभी नहीं हुई। माल आने तक पूंजी फंसी रहती है।",
        "Days from the transport bill (L/R) date to the day goods reached you.": "ट्रांसपोर्ट बिल्टी (L/R) तारीख से माल दुकान पर पहुंचने में लगा औसत समय।",
        "How many suppliers you bought from, and how much of your spend the biggest one holds.": "आपने कितने सप्लायरों से माल खरीदा, और शीर्ष सप्लायर की आपके कुल खर्च में कितनी हिस्सेदारी है।",
        "Physical volume that came in, regardless of price.": "दुकान में आया कुल भौतिक माल (गांठें एवं मीटर)।",
        "Everything has arrived": "सभी माल दुकान पर पहुंच चुका है",
        "No delivered consignments yet": "अभी कोई डिलीवर खेप नहीं है",
        "Metres not recorded": "मीटर दर्ज नहीं हैं",

        // Panels & Charts
        "How much you bought, month by month": "माह-दर-माह खरीदारी का विवरण",
        "The latest month may still be in progress.": "चालू माह अभी प्रगति पर हो सकता है।",
        "Who you buy from": "शीर्ष सप्लायर्स (आपूर्तिकर्ता)",
        "Share of total spend by supplier.": "कुल खर्च में आपूर्तिकर्ताओं की हिस्सेदारी का प्रतिशत।",
        "Where your money goes, by fabric": "कपड़े की किस्म के अनुसार खर्च",
        "Biggest spend first.": "सर्वाधिक खर्च के क्रम में।",
        "Show all": "सभी देखें",
        "Show fewer": "कम देखें",
        "All others": "अन्य सभी",

        // 90-Day Plan
        "Your 90-day plan": "आपकी 90-दिवसीय कार्ययोजना",
        "The AI's recommended order of work. Start on the left and move right.": "एआई द्वारा अनुशंसित प्राथमिकताओं का क्रम। बाएं से दाएं की ओर अमल करें।",
        "DAYS 1–30": "दिन 1–30: तत्काल कदम",
        "DAYS 31–60": "दिन 31–60: विस्तार एवं गति",
        "DAYS 61–90": "दिन 61–90: सुदृढ़ीकरण एवं लाभ",
        "Next steps": "आगामी कदम",

        // Full Analysis
        "Every detail is here — tap a topic to read it. Each shows the one-line gist first.": "विस्तृत रिपोर्ट यहां उपलब्ध है — पढ़ने के लिए किसी भी विषय पर टैप करें। प्रत्येक का मुख्य सार पहले दिखाया गया है।",
        "Every detail is here \u2014 tap a topic to read it. Each shows the one-line gist first.": "विस्तृत रिपोर्ट यहां उपलब्ध है — पढ़ने के लिए किसी भी विषय पर टैप करें। प्रत्येक का मुख्य सार पहले दिखाया गया है।",
        "Expand all": "सभी खोलें",
        "Collapse all": "सभी बंद करें",
        "Want the technical detail (data checks, how the advice was built)?": "क्या आप तकनीकी विवरण (डेटा सत्यापन, पाइपलाइन निष्पादन) देखना चाहते हैं?",
        "Open the detailed report": "विस्तृत तकनीकी रिपोर्ट खोलें",

        // Market Prices
        "What the market is charging": "बाजार में मौजूदा थोक भाव",
        "Indicative wholesale prices found online for fabrics like yours — use them to sanity-check what you pay.": "आपकी किस्म के कपड़ों के लिए ऑनलाइन मिले सांकेतिक थोक मूल्य — अपनी खरीद लागत की तुलना करें।",
        "Indicative wholesale prices found online for fabrics like yours \u2014 use them to sanity-check what you pay.": "आपकी किस्म के कपड़ों के लिए ऑनलाइन मिले सांकेतिक थोक मूल्य — अपनी खरीद लागत की तुलना करें।",
        "Fabric": "कपड़ा / किस्म",
        "Indicative price": "सांकेतिक थोक मूल्य",
        "Market": "मंडी / बाजार",
        "Source": "स्रोत",
        "Open": "देखें",
        "See source": "स्रोत देखें",
        "Prices are indicative and change daily. Always confirm with the supplier before ordering.": "भाव सांकेतिक हैं और प्रतिदिन बदल सकते हैं। आर्डर देने से पूर्व हमेशा सप्लायर से पुष्टि करें।",

        // History
        "Past refreshes": "पिछले विश्लेषण",
        "ledger entries reviewed": "बहीखाता प्रविष्टियों की समीक्षा की गई",
        "View report": "रिपोर्ट देखें",

        // Refresh Modal
        "Refresh insights": "सुझाव रिफ्रेश करें",
        "Generate my insights": "व्यापारिक सुझाव तैयार करें",
        "Refresh your insights": "नए व्यापारिक सुझाव प्राप्त करें",
        "We'll re-read your latest ledger, check today's market prices and rewrite your plan. It takes about 3 minutes. Insights can be refreshed once every 30 days.": "हम आपके नवीनतम बहीखाते का पुनरावलोकन करेंगे, आज के बाजार भाव जांचेंगे और आपकी कार्ययोजना को अपडेट करेंगे। इसमें लगभग 3 मिनट लगेंगे। सुझाव हर 30 दिन में एक बार अपडेट किए जा सकते हैं।",
        "Anything you want it to focus on?": "क्या आप किसी खास विषय पर ध्यान देना चाहते हैं?",
        "(optional)": "(वैकल्पिक)",
        "Grow festive sales": "त्योहारी सीजन में बिक्री बढ़ाएं",
        "Free up stuck money": "फंसी हुई पूंजी खाली करें",
        "Compete with Surat direct": "सूरत डायरेक्ट खरीद से मुकाबला",
        "Start refresh": "विश्लेषण शुरू करें",
        "Cancel": "रद्द करें",
        "Preparing your insights": "आपके सुझाव तैयार किए जा रहे हैं",
        "Reading your ledger…": "आपके बहीखाते का अध्ययन हो रहा है…",
        "Reading your ledger\u2026": "आपके बहीखाते का अध्ययन हो रहा है…",
        "Checking today’s market prices…": "आज के बाजार भाव जांचे जा रहे हैं…",
        "Checking today\u2019s market prices\u2026": "आज के बाजार भाव जांचे जा रहे हैं…",
        "Spotting what’s selling and what’s stuck…": "बिकने वाले और अटके माल की पहचान हो रही है…",
        "Spotting what\u2019s selling and what\u2019s stuck\u2026": "बिकने वाले और अटके माल की पहचान हो रही है…",
        "Writing your action plan…": "आपकी कार्ययोजना तैयार की जा रही है…",
        "Writing your action plan\u2026": "आपकी कार्ययोजना तैयार की जा रही है…",
        "Double-checking the advice against your numbers…": "आंकड़ों के साथ सुझावों का सत्यापन हो रहा है…",
        "Double-checking the advice against your numbers\u2026": "आंकड़ों के साथ सुझावों का सत्यापन हो रहा है…",
        "This takes about 3 minutes. Please keep this page open.": "इसमें लगभग 3 मिनट लगेंगे। कृपया इस पेज को खुला रखें।",

        // Empty states
        "No ledger entries to summarise yet": "संक्षेप के लिए अभी कोई बहीखाता प्रविष्टि नहीं है",
        "Your first insights are one click away": "आपके पहले व्यापारिक सुझाव बस एक क्लिक दूर हैं",
        "We'll read your ledger, compare your buying prices with the market and write a plain-English plan to help bring sales back up.": "हम आपके बहीखाते का अध्ययन करेंगे, बाजार के थोक भावों से तुलना करेंगे और बिक्री बढ़ाने के लिए व्यावहारिक कार्ययोजना तैयार करेंगे।",

        // Run Detail Page
        "Strategic Turnaround Brief": "रणनीतिक व्यावसायिक संक्षिप्त विवरण",
        "Executive Decision Brief": "कार्यकारी निर्णय सारांश",
        "Executive Business Decision Brief": "कार्यकारी निर्णय सारांश",
        "High-Impact Metric Highlights": "प्रमुख प्रभावकारी वित्तीय संकेतक",
        "Critical Business Bottlenecks": "गंभीर व्यापारिक अड़चनें",
        "Immediate Action Directives": "तत्काल कार्रवाई निर्देश",
        "Synthesized Insights": "संश्लेषित अंतर्दृष्टि",
        "Prompt Studio & Feedback Loop": "प्रॉम्प्ट स्टूडियो एवं प्रतिक्रिया",
        "Data & Market Telemetry": "डेटा एवं बाजार टेलीमेट्री",
        "Print / Export Brief": "प्रिंट / रिपोर्ट निर्यात",
        "Back to Dashboard": "डैशबोर्ड पर वापस जाएं",
        "Back to AI Dashboard": "एआई डैशबोर्ड पर वापस जाएं",
        "Grounding Score": "सत्यापन स्कोर",
        "Hallucination Risk": "भ्रम/विसंगति जोखिम",
        "Total Parcels": "कुल पार्सल",
        "Total Revenue": "कुल टर्नओवर",
        "Sales Records Analyzed": "बिक्री रिकॉर्ड का विश्लेषण",
        "Execution Latency": "प्रक्रिया समय",
        "Copy Brief": "रिपोर्ट कॉपी करें",
        "Copy Prompt": "प्रॉम्प्ट कॉपी करें",
        "Copied!": "कॉपी किया गया!",

        // Auth Gate
        "Admin Security Clearance": "व्यवस्थापक सुरक्षा सत्यापन",
        "Enter your Financial Year admin password to access proprietary AI insights and trade strategies.": "व्यापारिक रणनीतियों और एआई विश्लेषण तक पहुंचने के लिए अपना वित्तीय वर्ष पासवर्ड दर्ज करें।",
        "Admin Password": "व्यवस्थापक पासवर्ड",
        "Unlock Intelligence": "एआई विश्लेषण अनलॉक करें",
        "Return to Shop Ledger": "दुकान बहीखाते पर लौटें"
    };

    // Regex dynamic phrase translation rules for numbers/terms
    var DYNAMIC_RULES = [
        {
            regex: /^worth\s+(₹.+)$/i,
            replace: function (_, m1) { return m1 + ' मूल्य का'; }
        },
        {
            regex: /^(\d+[\d,.]*)\s+metres of fabric$/i,
            replace: function (_, m1) { return m1 + ' मीटर कपड़ा'; }
        },
        {
            regex: /^([\d.]+)%\s+of goods value$/i,
            replace: function (_, m1) { return 'माल मूल्य का ' + m1 + '%'; }
        },
        {
            regex: /^fastest\s+(\d+)d\s+·\s+slowest\s+(\d+)d$/i,
            replace: function (_, m1, m2) { return 'न्यूनतम ' + m1 + ' दिन · अधिकतम ' + m2 + ' दिन'; }
        },
        {
            regex: /^(\d+[\d,.]*)\s+days?$/i,
            replace: function (_, m1) { return m1 + ' दिन'; }
        },
        {
            regex: /^(.+?)\s*=\s*([\d.]+)%\s*of spend$/i,
            replace: function (_, m1, m2) { return m1 + ' = खर्च का ' + m2 + '%'; }
        },
        {
            regex: /^(\d+)\s+consignments?\s+on the road for over\s+(\d+)\s+days$/i,
            replace: function (_, m1, m2) { return m1 + ' खेप ' + m2 + ' दिनों से अधिक समय से रास्ते में'; }
        },
        {
            regex: /^Show all\s+(\d+)$/i,
            replace: function (_, m1) { return 'सभी ' + m1 + ' देखें'; }
        },
        {
            regex: /^Past refreshes\s*\((\d+)\)$/i,
            replace: function (_, m1) { return 'पिछले विश्लेषण (' + m1 + ')'; }
        },
        {
            regex: /^Next refresh in\s+(\d+)\s+days?$/i,
            replace: function (_, m1) { return 'अगला अपडेट ' + m1 + ' दिनों में'; }
        },
        {
            regex: /^(\d+)\s+ledger entries reviewed$/i,
            replace: function (_, m1) { return m1 + ' बहीखाता प्रविष्टियों की समीक्षा की गई'; }
        },
        {
            regex: /^(\d+)\s+entries auto-corrected$/i,
            replace: function (_, m1) { return m1 + ' प्रविष्टियां स्वतः सुधारी गईं'; }
        }
    ];

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function translateText(text) {
        if (!text) return text;
        var trimmed = text.trim();
        if (DICTIONARY[trimmed]) {
            return DICTIONARY[trimmed];
        }
        for (var i = 0; i < DYNAMIC_RULES.length; i++) {
            var rule = DYNAMIC_RULES[i];
            if (rule.regex.test(trimmed)) {
                return trimmed.replace(rule.regex, rule.replace);
            }
        }
        return null;
    }

    function getEmbeddedJson(id) {
        var el = document.getElementById(id);
        if (!el) return null;
        try {
            return JSON.parse(el.textContent);
        } catch (e) {
            return null;
        }
    }

    /**
     * Complete dual-data renderer:
     * Swaps all AI-generated content (Hero, Do This First, KPIs, Flags, Fabrics, 90-Day Plan, Full Analysis)
     * between English and Hindi with 0ms delay.
     */
    function renderDashboardBilingual(lang) {
        var statsEn = getEmbeddedJson('stats-en-data');
        var statsHi = getEmbeddedJson('stats-hi-data');
        var reportEn = getEmbeddedJson('report-en-data');
        var reportHi = getEmbeddedJson('report-hi-data');

        var activeReport = (lang === 'hi' && reportHi && reportHi.ok) ? reportHi : reportEn;
        var activeStats = (lang === 'hi' && statsHi && statsHi.has_data) ? statsHi : statsEn;

        // 1. Hero Big Picture Summary
        var heroSummaryEl = document.getElementById('heroSummary');
        if (heroSummaryEl && activeReport && activeReport.summary) {
            heroSummaryEl.textContent = activeReport.summary;
        }

        // 2. Hero Do This First Actions
        var heroActionsListEl = document.getElementById('heroActionsList');
        if (heroActionsListEl && activeReport && activeReport.first_actions && activeReport.first_actions.length) {
            var actHtml = '';
            activeReport.first_actions.forEach(function (a, idx) {
                actHtml += '<li>' +
                    '<span class="ix-num">' + (idx + 1) + '</span>' +
                    '<div><b>' + escapeHtml(a.lead) + '</b>' +
                    (a.detail ? '<span>' + escapeHtml(a.detail) + '</span>' : '') +
                    '</div></li>';
            });
            heroActionsListEl.innerHTML = actHtml;
        }

        // 3. KPI Cards
        var kpiContainerEl = document.getElementById('kpiContainer');
        if (kpiContainerEl && activeStats && activeStats.kpis && activeStats.kpis.length) {
            var kpiHtml = '';
            activeStats.kpis.forEach(function (k) {
                var trendIcon = '';
                if (k.trend === 'up') trendIcon = '<i class="fa-solid fa-arrow-trend-up"></i>';
                else if (k.trend === 'down') trendIcon = '<i class="fa-solid fa-arrow-trend-down"></i>';

                var sparkSvg = '';
                if (k.spark && k.spark.length) {
                    sparkSvg = '<svg class="ix-spark" data-values="' + k.spark.join(',') + '" aria-hidden="true"></svg>';
                }

                kpiHtml += '<article class="ix-kpi ix-tone-' + escapeHtml(k.tone) + '">' +
                    '<div class="ix-kpi-top">' +
                        '<div class="ix-kpi-label"><i class="fa-solid ' + escapeHtml(k.icon) + '"></i> <span class="kpi-label-text">' + escapeHtml(k.label) + '</span></div>' +
                        '<i class="fa-regular fa-circle-question ix-info" title="' + escapeHtml(k.hint) + '"></i>' +
                    '</div>' +
                    '<div class="ix-kpi-value">' + escapeHtml(k.value) + '</div>' +
                    '<div class="ix-kpi-sub">' +
                        trendIcon +
                        '<span>' + escapeHtml(k.sub) + '</span>' +
                    '</div>' +
                    sparkSvg +
                '</article>';
            });
            kpiContainerEl.innerHTML = kpiHtml;
            if (window.drawDashboardSparklines) {
                window.drawDashboardSparklines(kpiContainerEl);
            }
        }

        // 4. Watch List / Flags
        var flagsContainerEl = document.getElementById('flagsContainer');
        if (flagsContainerEl && activeStats && activeStats.flags) {
            var flagsHtml = '';
            activeStats.flags.forEach(function (f) {
                flagsHtml += '<div class="ix-watch-item ' + escapeHtml(f.level) + '">' +
                    '<i class="fa-solid ' + escapeHtml(f.icon) + '"></i>' +
                    '<div><b>' + escapeHtml(f.title) + '</b><span>' + escapeHtml(f.detail) + '</span></div>' +
                '</div>';
            });
            flagsContainerEl.innerHTML = flagsHtml;
        }

        // 5. Fabric Rank List
        var fabricRankEl = document.getElementById('fabricRankList');
        if (fabricRankEl && activeStats && activeStats.fabrics && activeStats.fabrics.length) {
            var fabHtml = '';
            activeStats.fabrics.forEach(function (f, idx) {
                var extraCls = (idx >= 5) ? 'ix-extra' : '';
                fabHtml += '<li class="' + extraCls + '">' +
                    '<span class="nm" title="' + escapeHtml(f.name) + '">' + escapeHtml(f.name) + '</span>' +
                    '<span class="vl">' + escapeHtml(f.value) + '<small>' + f.share + '%</small></span>' +
                    '<span class="ix-bar"><i data-w="' + f.bar + '" style="width:' + f.bar + '%"></i></span>' +
                '</li>';
            });
            fabricRankEl.innerHTML = fabHtml;
        }

        // 6. 90-Day Plan Phases
        var planContainerEl = document.getElementById('planContainer');
        if (planContainerEl && activeReport && activeReport.plan && activeReport.plan.length) {
            var planHtml = '';
            var defaultTitle = (lang === 'hi') ? 'आगामी कदम' : 'Next steps';
            activeReport.plan.slice(0, 3).forEach(function (p) {
                var actionsHtml = '';
                if (p.actions && p.actions.length) {
                    actionsHtml += '<ul>';
                    p.actions.forEach(function (a) {
                        actionsHtml += '<li><i class="fa-solid fa-circle-check"></i><div><b>' + escapeHtml(a.lead) + '</b>' +
                            (a.detail ? escapeHtml(a.detail) : '') + '</div></li>';
                    });
                    actionsHtml += '</ul>';
                }
                planHtml += '<article class="ix-phase">' +
                    '<span class="ix-phase-tag">' + escapeHtml(p.label) + '</span>' +
                    '<h3>' + escapeHtml(p.title || defaultTitle) + '</h3>' +
                    actionsHtml +
                '</article>';
            });
            planContainerEl.innerHTML = planHtml;
        }

        // 7. Full Analysis Accordion
        var accEl = document.getElementById('sectionsAccordion');
        if (accEl && activeReport && activeReport.sections && activeReport.sections.length) {
            var openKeys = {};
            accEl.querySelectorAll('.ix-acc-item.open').forEach(function (it) { openKeys[it.id] = true; });

            var accHtml = '';
            activeReport.sections.forEach(function (s) {
                var isOpen = !!openKeys[s.key];
                var openClass = isOpen ? ' open' : '';
                var expandedAttr = isOpen ? 'true' : 'false';
                var proseHtml = isOpen ? (window.renderMarkdownSafe ? window.renderMarkdownSafe(s.body) : '') : '';
                var proseDoneAttr = isOpen ? ' data-done="1"' : '';

                accHtml += '<article class="ix-acc-item' + openClass + '" id="' + escapeHtml(s.key) + '">' +
                    '<button type="button" class="ix-acc-head" aria-expanded="' + expandedAttr + '" aria-controls="' + escapeHtml(s.key) + '-body">' +
                        '<span class="ix-emoji" aria-hidden="true">' + escapeHtml(s.emoji) + '</span>' +
                        '<span class="ix-acc-text">' +
                            '<b>' + escapeHtml(s.title) + '</b>' +
                            (s.headline ? '<span>' + escapeHtml(s.headline) + '</span>' : '') +
                        '</span>' +
                        '<i class="fa-solid fa-chevron-down ix-chev" aria-hidden="true"></i>' +
                    '</button>' +
                    '<div class="ix-acc-body" id="' + escapeHtml(s.key) + '-body" role="region">' +
                        '<div class="ix-prose"' + proseDoneAttr + '>' + proseHtml + '</div>' +
                        '<div class="ix-md-src" hidden>' + escapeHtml(s.body) + '</div>' +
                    '</div>' +
                '</article>';
            });
            accEl.innerHTML = accHtml;
            if (window.bindDashboardAccordions) {
                window.bindDashboardAccordions();
            }
        }
    }

    var currentLang = 'en';

    function getStoredLanguage() {
        try {
            return localStorage.getItem(STORAGE_KEY) || 'en';
        } catch (e) {
            return 'en';
        }
    }

    function setStoredLanguage(lang) {
        try {
            localStorage.setItem(STORAGE_KEY, lang);
        } catch (e) {}
    }

    function applyLanguage(lang) {
        currentLang = (lang === 'hi') ? 'hi' : 'en';
        document.documentElement.lang = currentLang;

        // 1. Update Toggle Button UI state
        var toggle = document.getElementById('intelLangToggle');
        if (toggle) {
            var enOpts = toggle.querySelectorAll('[data-lang="en"]');
            var hiOpts = toggle.querySelectorAll('[data-lang="hi"]');
            enOpts.forEach(function (el) { el.classList.toggle('active', currentLang === 'en'); });
            hiOpts.forEach(function (el) { el.classList.toggle('active', currentLang === 'hi'); });
            toggle.setAttribute('aria-label', currentLang === 'en' ? 'Switch to Hindi' : 'अंग्रेजी में देखें');
        }

        // 2. Render dual datasets if on Dashboard
        renderDashboardBilingual(currentLang);

        // 3. Render all declarative [data-en][data-hi] nodes
        var declarativeNodes = document.querySelectorAll('[data-en][data-hi]');
        declarativeNodes.forEach(function (el) {
            var val = (currentLang === 'hi') ? el.getAttribute('data-hi') : el.getAttribute('data-en');
            if (val !== null && val !== undefined) {
                if (val.indexOf('<') !== -1) {
                    el.innerHTML = val;
                } else {
                    el.textContent = val;
                }
            }
        });

        // 4. Dynamic Greeting
        var h = new Date().getHours();
        var g = document.getElementById('greeting');
        if (g) {
            if (currentLang === 'hi') {
                g.textContent = h < 12 ? (g.dataset.morningHi || 'सुप्रभात') : h < 17 ? (g.dataset.afternoonHi || 'शुभ दोपहर') : (g.dataset.eveningHi || 'शुभ संध्या');
            } else {
                g.textContent = h < 12 ? (g.dataset.morningEn || 'Good morning') : h < 17 ? (g.dataset.afternoonEn || 'Good afternoon') : (g.dataset.eveningEn || 'Good evening');
            }
        }

        // 5. Toggle buttons with count (Show all / Show fewer)
        document.querySelectorAll('[data-toggle]').forEach(function (btn) {
            var box = document.querySelector(btn.dataset.toggle);
            var isOpen = box && box.classList.contains('ix-open');
            var total = btn.dataset.total || btn.textContent.replace(/[^0-9]/g, '');
            if (currentLang === 'hi') {
                btn.textContent = isOpen ? 'कम देखें' : 'सभी ' + total + ' देखें';
            } else {
                btn.textContent = isOpen ? 'Show fewer' : 'Show all ' + total;
            }
        });

        // 6. Detailed Run Page: render appropriate markdown source (EN vs HI)
        var rawElHi = document.getElementById('rawMarkdownContentHi');
        var rawElEn = document.getElementById('rawMarkdownContentEn') || document.getElementById('rawMarkdownContent');
        var targetReportEl = document.getElementById('renderedReportProse');
        if (targetReportEl && window.renderMarkdownSafe) {
            var md = (currentLang === 'hi' && rawElHi && rawElHi.textContent.trim()) ? rawElHi.textContent.trim() : (rawElEn ? rawElEn.textContent.trim() : '');
            if (md) {
                targetReportEl.innerHTML = window.renderMarkdownSafe(md);
            }
        }

        // 7. Fallback DOM translation for base layout / navbar / brand
        var baseSelectors = [
            '.brand-title span:first-child',
            '.brand-tag',
            '.btn-legacy span',
            '.btn-lock span',
            '.intel-footer div span',
            '.auth-title',
            '.auth-desc',
            '.auth-label',
            '.btn-auth span',
            '.btn-back-link span',
            '.detail-tab-btn span',
            '.btn-action-outline span'
        ];
        var baseNodes = document.querySelectorAll(baseSelectors.join(','));
        baseNodes.forEach(function (node) {
            if (node.closest('pre') || node.closest('code') || node.tagName === 'SCRIPT') return;
            if (!node.dataset.originalEn) {
                node.dataset.originalEn = node.textContent.trim();
            }
            if (currentLang === 'hi') {
                var translated = translateText(node.dataset.originalEn);
                if (translated) node.textContent = translated;
            } else {
                if (node.dataset.originalEn) node.textContent = node.dataset.originalEn;
            }
        });

        // 8. Tooltips
        var titledNodes = document.querySelectorAll('[title]');
        titledNodes.forEach(function (node) {
            if (!node.dataset.originalTitle) {
                node.dataset.originalTitle = node.getAttribute('title');
            }
            if (currentLang === 'hi') {
                var trans = translateText(node.dataset.originalTitle);
                if (trans) node.setAttribute('title', trans);
            } else {
                if (node.dataset.originalTitle) node.setAttribute('title', node.dataset.originalTitle);
            }
        });

        // 9. Notify charts and external modules
        try {
            window.dispatchEvent(new CustomEvent('intelligenceLanguageChanged', { detail: { lang: currentLang } }));
        } catch (e) {}
    }

    function toggleLanguage() {
        var next = (currentLang === 'en') ? 'hi' : 'en';
        setStoredLanguage(next);
        applyLanguage(next);
    }

    // Expose API
    window.toggleIntelligenceLanguage = toggleLanguage;
    window.setIntelligenceLanguage = function (lang) {
        setStoredLanguage(lang);
        applyLanguage(lang);
    };
    window.getIntelligenceLanguage = function () {
        return currentLang;
    };
    window.translateIntelligenceText = translateText;

    // Auto-initialize on DOM ready
    function init() {
        var initialLang = getStoredLanguage();
        applyLanguage(initialLang);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})(window, document);
