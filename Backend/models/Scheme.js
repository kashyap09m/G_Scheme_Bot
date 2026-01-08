const mongoose = require('mongoose');

const SchemeSchema = new mongoose.Schema({
  title: {
    type: String,
    required: [true, 'Please add a title'],
    trim: true,
  },
  description: {
    type: String,
    required: [true, 'Please add a short description'],
  },
  full_details: {
    type: String,
    required: [true, 'Please add full details about the scheme'],
  },
  eligibility: {
    age_min: { type: Number, default: 0 },
    age_max: { type: Number, default: 100 },
    profession: { type: [String], default: ['Any'] },
    gender: { type: [String], default: ['Any'] },
    salary_max: { type: Number, default: 10000000 }, // Max annual salary
    state: { type: [String], default: ['National'] }, // e.g., ["National"] or ["Maharashtra", "Gujarat"]
  },
  required_documents: {
    type: [String],
    required: true,
  },
  benefits: {
    type: String,
    required: [true, 'Please list the benefits'],
  },
  website_link: {
    type: String,
    default: '#',
    match: [
      /^(https|http):\/\/[^\s/$.?#].[^\s]*$|^#$/,
      'Please use a valid URL or #',
    ],
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

module.exports = mongoose.model('Scheme', SchemeSchema);
