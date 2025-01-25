const Example = require('../models/exampleModel');

// Get Example Data
exports.getExample = async (req, res, next) => {
    try {
        const examples = await Example.find();
        res.json(examples);
    } catch (err) {
        next(err);
    }
};

// Create Example Data
exports.createExample = async (req, res, next) => {
    try {
        const example = new Example(req.body);
        const savedExample = await example.save();
        res.status(201).json(savedExample);
    } catch (err) {
        next(err);
    }
};
