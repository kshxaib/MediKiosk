export interface TranslationDict {
  // Steps
  stepLanguage: string
  stepMobile: string
  stepRegister: string
  stepFace: string
  stepConsent: string
  stepStream: string
  stepDepartment: string
  stepReady: string

  // Common
  patient: string
  patientCode: string
  age: string
  gender: string
  male: string
  female: string
  other: string
  continue: string
  back: string
  retry: string
  finish: string
  loading: string

  // Mobile Page
  mobileTitle: string
  mobileSubtitle: string
  mobilePlaceholder: string
  mobileLookupBtn: string
  mobileSearching: string
  existingPatientFound: string
  noPatientFound: string
  notRegisteredDesc: string
  registerNewBtn: string
  proceedToFaceBtn: string
  invalidMobileError: string

  // Register Page
  regTitle: string
  regSubtitle: string
  fullNameLabel: string
  fullNamePlaceholder: string
  dobLabel: string
  ageLabel: string
  genderLabel: string
  selectGender: string
  emailLabel: string
  emailPlaceholder: string
  registerAndProceedBtn: string
  registeringBtn: string

  // Face Page
  faceEnrollTitle: string
  faceVerifyTitle: string
  faceOvalPrompt: string
  faceCaptureEnrollBtn: string
  faceCaptureVerifyBtn: string
  faceProcessingEnroll: string
  faceProcessingVerify: string
  faceVerifiedTitle: string
  faceVerifiedDesc: string
  faceEnrolledTitle: string
  faceEnrolledDesc: string
  faceFailedTitle: string
  faceFailedDesc: string
  faceErrorTitle: string
  faceNoFaceDetected: string
  proceedToConsentBtn: string
  cameraUnavailable: string

  // Consent Page
  consentTitle: string
  consentSummary: string
  consentPt1: string
  consentPt2: string
  consentPt3: string
  consentPt4: string
  consentStatement: string
  consentAgreeBtn: string
  consentDeclineBtn: string
  consentDeclinedTitle: string
  consentDeclinedDesc: string
  returnHomeBtn: string

  // Stream Page
  streamTitle: string
  streamSubtitle: string
  selectStreamBtn: string
  modernMedicineName: string
  modernMedicineDesc: string
  ayushName: string
  ayushDesc: string

  // Department Page
  departmentTitle: string
  departmentSubtitle: string
  selectedStreamLabel: string
  chooseDepartmentBtn: string

  // Ready Page
  readyTitle: string
  readySubtitle: string
  sessionStatus: string
  startInterviewBtn: string
  sessionActiveStatus: string
  nextPhaseNotice: string

  // Department Names & Descs
  deptNames: Record<string, { name: string; desc: string }>
}

export const translations: Record<'en' | 'hi', TranslationDict> = {
  en: {
    stepLanguage: 'Step 1: Language Selection',
    stepMobile: 'Step 2: Patient Identification',
    stepRegister: 'Step 2: New Patient Registration',
    stepFace: 'Step 3: Biometric Face Verification',
    stepConsent: 'Step 4: Clinical Consent',
    stepStream: 'Step 5: Medical Stream Selection',
    stepDepartment: 'Step 6: Department Selection',
    stepReady: 'Step 7: Intake Session Initialized',

    patient: 'Patient',
    patientCode: 'Patient Code',
    age: 'Age',
    gender: 'Gender',
    male: 'Male',
    female: 'Female',
    other: 'Other',
    continue: 'Continue',
    back: 'Back',
    retry: 'Retry Capture',
    finish: 'Finish & Return to Home',
    loading: 'Loading...',

    mobileTitle: 'Patient Mobile Identification',
    mobileSubtitle: 'Enter your 10-digit mobile number to lookup your hospital record or register.',
    mobilePlaceholder: 'Enter 10-digit mobile number (e.g. 9876543210)',
    mobileLookupBtn: 'Verify Mobile Number →',
    mobileSearching: 'Searching hospital records...',
    existingPatientFound: 'Existing Patient Record Found',
    noPatientFound: 'No Patient Record Found',
    notRegisteredDesc: 'This mobile number is not yet registered in the hospital database.',
    registerNewBtn: 'Register as New Patient →',
    proceedToFaceBtn: 'Proceed to Webcam Face Verification →',
    invalidMobileError: 'Please enter a valid 10-digit Indian mobile number',

    regTitle: 'New Patient Registration',
    regSubtitle: 'Please enter your details to create your hospital patient profile.',
    fullNameLabel: 'Full Name *',
    fullNamePlaceholder: 'e.g. Rajesh Kumar',
    dobLabel: 'Date of Birth (Optional)',
    ageLabel: 'Age (Years)',
    genderLabel: 'Gender',
    selectGender: 'Select Gender',
    emailLabel: 'Email Address (Optional)',
    emailPlaceholder: 'e.g. rajesh@example.com',
    registerAndProceedBtn: 'Register & Proceed to Biometric Face Enrollment →',
    registeringBtn: 'Registering Patient...',

    faceEnrollTitle: 'Enroll Your Face Biometric',
    faceVerifyTitle: 'Verify Your Identity',
    faceOvalPrompt: 'Position your face within the oval guide and look at the camera.',
    faceCaptureEnrollBtn: '📸 Capture & Enroll Biometric Face',
    faceCaptureVerifyBtn: '📸 Capture & Verify Identity',
    faceProcessingEnroll: 'Detecting face & extracting ArcFace biometric embedding...',
    faceProcessingVerify: 'Running ArcFace biometric comparison...',
    faceVerifiedTitle: 'Identity Verified Successfully',
    faceVerifiedDesc: 'Biometric face match confirmed via InsightFace ArcFace comparison.',
    faceEnrolledTitle: 'Biometric Face Enrolled',
    faceEnrolledDesc: 'Your face embedding has been securely stored for future instant check-ins.',
    faceFailedTitle: 'Face Not Matched — Verification Failed',
    faceFailedDesc: 'The captured face does not match the enrolled biometric profile. Please try again.',
    faceErrorTitle: 'Verification Error',
    faceNoFaceDetected: 'No face was detected. Please position your face clearly in good lighting.',
    proceedToConsentBtn: 'Proceed to Patient Consent →',
    cameraUnavailable: 'Webcam is unavailable. Please grant camera permissions in your browser.',

    consentTitle: 'Patient Clinical Intake & Data Processing Consent',
    consentSummary: 'To provide you with an intelligent self-service consultation, MediKiosk will collect your clinical symptoms, health history, and vital signs, summarize them securely, and route the case to your attending doctor.',
    consentPt1: 'Your health data is stored securely in compliance with hospital confidentiality standards.',
    consentPt2: 'AI assists with structured clinical history organization and question collection.',
    consentPt3: 'The AI does NOT replace a medical doctor. Final clinical decisions are made by licensed doctors.',
    consentPt4: 'You may withdraw consent at any time and visit the standard hospital reception counter.',
    consentStatement: 'I hereby give my explicit and informed consent to participate in this automated clinical intake assessment.',
    consentAgreeBtn: '✓ I Agree & Grant Consent',
    consentDeclineBtn: 'Decline',
    consentDeclinedTitle: 'Consent Declined',
    consentDeclinedDesc: 'You have chosen not to proceed with self-service intake. Your session has been cancelled. Please visit the front reception desk for manual check-in.',
    returnHomeBtn: 'Return to Home',

    streamTitle: 'Select Medical Stream',
    streamSubtitle: 'Choose whether you would like an allopathic (Modern Medicine) or traditional Ayurvedic consultation.',
    selectStreamBtn: 'Select Stream →',
    modernMedicineName: 'Modern Medicine (Allopathy)',
    modernMedicineDesc: 'MBBS clinical assessment: symptoms, duration, history of illness, and systemic review.',
    ayushName: 'AYUSH / Ayurveda',
    ayushDesc: 'Traditional Ayurvedic assessment: Prakriti, Agni, Dosha imbalances, and holistic wellness.',

    departmentTitle: 'Select Clinical Department',
    departmentSubtitle: 'Choose the relevant medical department for your symptoms.',
    selectedStreamLabel: 'Selected Stream',
    chooseDepartmentBtn: 'Choose Department →',

    readyTitle: 'Ready for Clinical Interview',
    readySubtitle: 'Intake session created, patient identity verified, consent granted, and department selected.',
    sessionStatus: 'Session Status',
    startInterviewBtn: '🚀 Start Active Session (Status: INTERVIEW_ACTIVE)',
    sessionActiveStatus: '✓ Session is now INTERVIEW_ACTIVE (Ready for Phase 5 AI Interview)',
    nextPhaseNotice: 'Phase 4 session state machine initialized. In Phase 5, the adaptive AI interview and speech recognition will be connected to this session.',

    deptNames: {
      GEN_MED: {
        name: 'General Medicine',
        desc: 'Fever, cough, infections, diabetes, hypertension, and general symptoms',
      },
      CARDIO: {
        name: 'Cardiology',
        desc: 'Chest discomfort, heart palpitations, blood pressure, breathlessness',
      },
      NEURO: {
        name: 'Neurology',
        desc: 'Headaches, migraines, dizziness, numbness, tremors, seizure evaluation',
      },
      ORTHO: {
        name: 'Orthopedics',
        desc: 'Joint pain, knee/back pain, fractures, arthritis, mobility difficulties',
      },
      DERMA: {
        name: 'Dermatology',
        desc: 'Skin rashes, allergies, acne, itching, hair and nail conditions',
      },
      AYURVEDA: {
        name: 'Ayurveda & Panchakarma',
        desc: 'Constitutional balance, chronic digestion, Vata/Pitta/Kapha wellness',
      },
    },
  },

  hi: {
    stepLanguage: 'चरण 1: भाषा चयन',
    stepMobile: 'चरण 2: रोगी पहचान (मोबाइल नंबर)',
    stepRegister: 'चरण 2: नया रोगी पंजीकरण',
    stepFace: 'चरण 3: बायोमेट्रिक चेहरा सत्यापन',
    stepConsent: 'चरण 4: नैदानिक सहमति',
    stepStream: 'चरण 5: चिकित्सा पद्धति चयन',
    stepDepartment: 'चरण 6: विभाग चयन',
    stepReady: 'चरण 7: परामर्श सत्र तैयार',

    patient: 'रोगी',
    patientCode: 'रोगी कोड',
    age: 'आयु',
    gender: 'लिंग',
    male: 'पुरुष',
    female: 'महिला',
    other: 'अन्य',
    continue: 'आगे बढ़ें',
    back: 'पीछे जाएं',
    retry: 'पुनः प्रयास करें',
    finish: 'समाप्त कर मुख्य पृष्ठ पर जाएं',
    loading: 'लोड हो रहा है...',

    mobileTitle: 'रोगी मोबाइल पहचान',
    mobileSubtitle: 'अस्पताल रिकॉर्ड खोजने या नया पंजीकरण करने हेतु अपना 10 अंकों का मोबाइल नंबर दर्ज करें।',
    mobilePlaceholder: '10 अंकों का मोबाइल नंबर दर्ज करें (उदा. 9876543210)',
    mobileLookupBtn: 'मोबाइल नंबर सत्यापित करें →',
    mobileSearching: 'अस्पताल रिकॉर्ड खोजा जा रहा है...',
    existingPatientFound: 'पंजीकृत रोगी रिकॉर्ड उपलब्ध है',
    noPatientFound: 'कोई पूर्व रिकॉर्ड नहीं मिला',
    notRegisteredDesc: 'यह मोबाइल नंबर अस्पताल डेटाबेस में पंजीकृत नहीं है।',
    registerNewBtn: 'नए रोगी के रूप में पंजीकरण करें →',
    proceedToFaceBtn: 'वेबकैम चेहरा सत्यापन के लिए आगे बढ़ें →',
    invalidMobileError: 'कृपया एक मान्य 10-अंकीय भारतीय मोबाइल नंबर दर्ज करें',

    regTitle: 'नया रोगी पंजीकरण',
    regSubtitle: 'अस्पताल में नया रोगी रिकॉर्ड बनाने हेतु कृपया अपनी जानकारी दर्ज करें।',
    fullNameLabel: 'पूरा नाम *',
    fullNamePlaceholder: 'उदा. राजेश कुमार',
    dobLabel: 'जन्म तिथि (वैकल्पिक)',
    ageLabel: 'आयु (वर्ष)',
    genderLabel: 'लिंग',
    selectGender: 'लिंग चुनें',
    emailLabel: 'ईमेल पता (वैकल्पिक)',
    emailPlaceholder: 'उदा. rajesh@example.com',
    registerAndProceedBtn: 'पंजीकरण करें एवं चेहरा बायोमेट्रिक के लिए आगे बढ़ें →',
    registeringBtn: 'पंजीकरण हो रहा है...',

    faceEnrollTitle: 'अपना चेहरा बायोमेट्रिक दर्ज करें',
    faceVerifyTitle: 'अपनी पहचान सत्यापित करें',
    faceOvalPrompt: 'कृपया अपना चेहरा अंडाकार घेरे के अंदर रखें और कैमरे की ओर देखें।',
    faceCaptureEnrollBtn: '📸 चेहरा कैप्चर एवं बायोमेट्रिक दर्ज करें',
    faceCaptureVerifyBtn: '📸 चेहरा कैप्चर एवं पहचान सत्यापित करें',
    faceProcessingEnroll: 'चेहरे का बायोमेट्रिक एम्बेडिंग निकाला जा रहा है...',
    faceProcessingVerify: 'आर्कफेस बायोमेट्रिक मिलान की प्रक्रिया जारी है...',
    faceVerifiedTitle: 'पहचान सफलतापूर्वक सत्यापित हुई',
    faceVerifiedDesc: 'इनसाइटफेस आर्कफेस द्वारा चेहरे का बायोमेट्रिक मिलान सफल रहा।',
    faceEnrolledTitle: 'चेहरा बायोमेट्रिक सफलतापूर्वक दर्ज हुआ',
    faceEnrolledDesc: 'भविष्य में त्वरित जांच हेतु आपका बायोमेट्रिक सुरक्षित रूप से दर्ज कर लिया गया है।',
    faceFailedTitle: 'चेहरा मेल नहीं खाया — सत्यापन असफल',
    faceFailedDesc: 'कैप्चर किया गया चेहरा पंजीकृत बायोमेट्रिक से मेल नहीं खाता। कृपया पुनः प्रयास करें।',
    faceErrorTitle: 'सत्यापन में त्रुटि',
    faceNoFaceDetected: 'कोई चेहरा नहीं मिला। कृपया अच्छी रोशनी में चेहरे को सीधे कैमरे के सामने रखें।',
    proceedToConsentBtn: 'नैदानिक सहमति के लिए आगे बढ़ें →',
    cameraUnavailable: 'कैमरा उपलब्ध नहीं है। कृपया ब्राउज़र में कैमरा अनुमति दें।',

    consentTitle: 'रोगी नैदानिक सहमति एवं डेटा प्रसंस्करण',
    consentSummary: 'आपको त्वरित एवं आधुनिक परामर्श सुविधा प्रदान करने हेतु, मेडीकियोस्क आपके लक्षणों, स्वास्थ्य इतिहास और विटल्स को संकलित कर डॉक्टर को प्रस्तुत करेगा।',
    consentPt1: 'आपकी स्वास्थ्य जानकारी अस्पताल की गोपनीयता और सुरक्षा नीति के अनुसार सुरक्षित रखी जाएगी।',
    consentPt2: 'एआई केवल व्यवस्थित लक्षण संकलन और संक्षिप्त रिपोर्ट तैयार करने में सहायता करता है।',
    consentPt3: 'एआई डॉक्टर का विकल्प नहीं है। अंतिम निदान एवं उपचार केवल योग्य चिकित्सक द्वारा किया जाएगा।',
    consentPt4: 'आप किसी भी समय सहमति अस्वीकार कर सामान्य ओपीडी काउंटर पर परामर्श ले सकते हैं।',
    consentStatement: 'मैं इस स्वचालित नैदानिक मूल्यांकन में भाग लेने हेतु अपनी स्पष्ट एवं सूचित सहमति प्रदान करता/करती हूँ।',
    consentAgreeBtn: '✓ मैं सहमत हूँ एवं सहमति प्रदान करता हूँ',
    consentDeclineBtn: 'अस्वीकार करें',
    consentDeclinedTitle: 'सहमति अस्वीकार की गई',
    consentDeclinedDesc: 'आपने कियोस्क मूल्यांकन में भाग न लेने का निर्णय लिया है। आपका सत्र रद्द कर दिया गया है। कृपया मुख्य पंजीकरण काउंटर पर संपर्क करें।',
    returnHomeBtn: 'मुख्य पृष्ठ पर जाएं',

    streamTitle: 'चिकित्सा पद्धति चुनें',
    streamSubtitle: 'कृपया चुनें कि आप आधुनिक चिकित्सा (एलोपैथी) अथवा पारंपरिक आयुर्वेदिक परामर्श लेना चाहते हैं।',
    selectStreamBtn: 'पद्धति चुनें →',
    modernMedicineName: 'आधुनिक चिकित्सा (Modern Medicine / Allopathy)',
    modernMedicineDesc: 'एमबीबीएस आधारित नैदानिक मूल्यांकन: लक्षण, अवधि, पूर्व बीमारी एवं शारीरिक परीक्षण।',
    ayushName: 'आयुष / आयुर्वेद (AYUSH / Ayurveda)',
    ayushDesc: 'पारंपरिक आयुर्वेदिक पद्धति: प्रकृति, अग्नि, दोष असंतुलन एवं समग्र स्वास्थ्य परामर्श।',

    departmentTitle: 'नैदानिक विभाग चुनें',
    departmentSubtitle: 'अपनी बीमारी अथवा लक्षणों के अनुसार उपयुक्त विभाग का चयन करें।',
    selectedStreamLabel: 'चयनित पद्धति',
    chooseDepartmentBtn: 'विभाग चुनें →',

    readyTitle: 'परामर्श हेतु तैयार',
    readySubtitle: 'परामर्श सत्र तैयार है, पहचान सत्यापित हो चुकी है, सहमति प्राप्त है और विभाग चुना जा चुका है।',
    sessionStatus: 'सत्र स्थिति',
    startInterviewBtn: '🚀 सक्रिय सत्र शुरू करें (स्थिति: INTERVIEW_ACTIVE)',
    sessionActiveStatus: '✓ सत्र अब सक्रिय है (फेज 5 एआई इंटरव्यू हेतु तैयार)',
    nextPhaseNotice: 'फेज 4 सत्र प्रबंधन पूरा हो चुका है। फेज 5 में एआई प्रश्नोत्तरी एवं आवाज पहचान प्रणाली को इस सत्र से जोड़ा जाएगा।',

    deptNames: {
      GEN_MED: {
        name: 'सामान्य चिकित्सा (General Medicine)',
        desc: 'बुखार, खांसी, संक्रमण, मधुमेह (शुगर), रक्तचाप और सामान्य स्वास्थ्य समस्याएं',
      },
      CARDIO: {
        name: 'हृदय रोग विभाग (Cardiology)',
        desc: 'सीने में दर्द, दिल की धड़कन तेज होना, हाई बीपी, सांस फूलना',
      },
      NEURO: {
        name: 'तंत्रिका रोग विभाग (Neurology)',
        desc: 'सिरदर्द, माइग्रेन, चक्कर आना, सुन्नपन, कंपकंपी, मिर्गी की समस्या',
      },
      ORTHO: {
        name: 'हड्डी एवं जोड़ रोग (Orthopedics)',
        desc: 'जोड़ों का दर्द, घुटने/कमर का दर्द, फ्रैक्चर, गठिया, चलने में परेशानी',
      },
      DERMA: {
        name: 'त्वचा एवं एलर्जी रोग (Dermatology)',
        desc: 'त्वचा पर चकत्ते, खुजली, कील-मुंहासे, एलर्जी, बाल और नाखून की समस्याएं',
      },
      AYURVEDA: {
        name: 'आयुर्वेद एवं पंचकर्म (Ayurveda & Panchakarma)',
        desc: 'दोष संतुलन, पाचन विकार, वात-पित्त-कफ असंतुलन, प्राकृतिक उपचार',
      },
    },
  },
}

export function useTranslation(language: string): TranslationDict {
  const langKey = language === 'hi' ? 'hi' : 'en'
  return translations[langKey]
}