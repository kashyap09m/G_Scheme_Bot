// const Scheme = require('../models/Scheme'); // Would use this with a real DB
// const User = require('../models/User'); // Would use this for recommendations

// --- MOCK DATABASE ---
// This array simulates the data that would be in your MongoDB collection.
const FAKE_DB_SCHEMES = [
  {
    _id: "60c72b965f1b2c001f8e4d3a",
    title: "Pradhan Mantri Jan Dhan Yojana (PMJDY)",
    description: "National Mission for Financial Inclusion.",
    full_details: "PMJDY provides access to financial services like bank accounts, remittance, credit, insurance, and pension. Account holders get a RuPay debit card and accident insurance.",
    eligibility: {
      age_min: 18,
      age_max: 65,
      profession: ["Any"],
      gender: ["Any"],
      salary_max: 10000000,
      state: ["National"]
    },
    required_documents: ["Aadhaar Card", "PAN Card", "Passport Size Photo"],
    benefits: "Zero balance account, accident insurance cover, overdraft facility.",
    website_link: "https://pmjdy.gov.in/"
  },
  {
    _id: "60c72b965f1b2c001f8e4d3b",
    title: "Student Startup Scheme (Maharashtra)",
    description: "Provides funding and mentorship for student-led startups.",
    full_details: "This scheme, specific to Maharashtra, aims to foster innovation by providing seed funding and incubation support to students in colleges and universities.",
    eligibility: {
      age_min: 16,
      age_max: 25,
      profession: ["Student"],
      gender: ["Any"],
      salary_max: 1000000,
      state: ["Maharashtra"]
    },
    required_documents: ["Aadhaar Card", "Student ID Card", "Business Proposal", "College Bonafide Certificate"],
    benefits: "Seed funding up to ₹2,00,000, mentorship, access to incubators.",
    website_link: "#"
  },
  {
    _id: "60c72b965f1b2c001f8e4d3c",
    title: "PM-KISAN Scheme",
    description: "Financial support for farmers.",
    full_details: "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) provides income support of ₹6,000 per year in three equal installments to all landholding farmer families.",
    eligibility: {
      age_min: 18,
      age_max: 70,
      profession: ["Farmer"],
      gender: ["Any"],
      salary_max: 200000,
      state: ["National"]
    },
    required_documents: ["Aadhaar Card", "PAN Card", "Land Ownership Documents"],
    benefits: "₹6,000 per year directly to the bank account.",
    website_link: "https://pmkisan.gov.in/"
  }
];

// --- Controller Functions ---

// @desc    Get all schemes
// @route   GET /api/schemes
exports.getSchemes = async (req, res, next) => {
  try {
    // Real DB query: const schemes = await Scheme.find();
    
    // Mock query:
    const schemes = FAKE_DB_SCHEMES;
    
    res.status(200).json({ success: true, count: schemes.length, data: schemes });
  } catch (err) {
    res.status(500).json({ success: false, error: 'Server Error' });
  }
};

// @desc    Get single scheme by ID
// @route   GET /api/schemes/:id
exports.getSchemeById = async (req, res, next) => {
  try {
    // Real DB query: const scheme = await Scheme.findById(req.params.id);
    
    // Mock query:
    const scheme = FAKE_DB_SCHEMES.find(s => s._id === req.params.id);

    if (!scheme) {
      return res.status(404).json({ success: false, error: 'Scheme not found' });
    }
    
    res.status(200).json({ success: true, data: scheme });
  } catch (err) {
    res.status(500).json({ success: false, error: 'Server Error' });
  }
};

// @desc    Get schemes by state
// @route   GET /api/schemes/state/:stateName
exports.getSchemesByState = async (req, res, next) => {
  try {
    const stateName = req.params.stateName.toLowerCase();

    // Real DB query:
    // const schemes = await Scheme.find({
    //   'eligibility.state': { $in: [new RegExp(stateName, 'i'), 'National'] }
    // });
    
    // Mock query:
    const schemes = FAKE_DB_SCHEMES.filter(s => {
      const stateList = s.eligibility.state.map(st => st.toLowerCase());
      return stateList.includes(stateName) || stateList.includes('national');
    });

    res.status(200).json({ success: true, count: schemes.length, data: schemes });
  } catch (err) {
    res.status(500).json({ success: false, error: 'Server Error' });
  }
};


// @desc    Get recommended schemes for a user
// @route   GET /api/schemes/recommend
exports.getRecommendedSchemes = async (req, res, next) => {
  try {
    // --- MOCK USER ---
    // In a real app, this user would come from `req.user` (via protected middleware)
    // const user = await User.findById(req.user.id);
    const mockUser = {
      age: 20,
      profession: "Student",
      gender: "Male",
      salary: 0,
      state: "Maharashtra"
    };
    
    // --- MOCK RECOMMENDATION LOGIC ---
    // Real DB query:
    // const recommendedSchemes = await Scheme.find({
    //   'eligibility.age_min': { $lte: mockUser.age },
    //   'eligibility.age_max': { $gte: mockUser.age },
    //   'eligibility.profession': { $in: [mockUser.profession, 'Any'] },
    //   'eligibility.gender': { $in: [mockUser.gender, 'Any'] },
    //   'eligibility.salary_max': { $gte: mockUser.salary },
    //   'eligibility.state': { $in: [mockUser.state, 'National'] }
    // });
    
    // Mock logic using our fake DB:
    const recommendedSchemes = FAKE_DB_SCHEMES.filter(scheme => {
      const el = scheme.eligibility;
      const stateList = el.state.map(st => st.toLowerCase());

      const ageMatch = mockUser.age >= el.age_min && mockUser.age <= el.age_max;
      const professionMatch = el.profession.includes(mockUser.profession) || el.profession.includes("Any");
      const genderMatch = el.gender.includes(mockUser.gender) || el.gender.includes("Any");
      const salaryMatch = mockUser.salary <= el.salary_max;
      const stateMatch = stateList.includes(mockUser.state.toLowerCase()) || stateList.includes("national");
      
      return ageMatch && professionMatch && genderMatch && salaryMatch && stateMatch;
    });

    res.status(200).json({ success: true, count: recommendedSchemes.length, data: recommendedSchemes });

  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, error: 'Server Error' });
  }
};