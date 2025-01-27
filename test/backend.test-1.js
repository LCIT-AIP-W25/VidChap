import request from 'supertest';
import { assert } from 'chai';
import app from '../backend/da.js';  // Ensure the correct import

process.env.PORT = 3001;  // Use a different port for the test

describe('Backend API Tests', function () {
  
  // Test for valid YouTube URL
  it('should return success for a valid YouTube URL', function (done) {
    const validUrl = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';  // Example YouTube URL

    request(app)
      .post('/download-audio')
      .send({ url: validUrl })
      .expect('Content-Type', /json/)
      .expect(200)
      .end((err, res) => {
        if (err) return done(err);
        
        // Assert the response structure and content
        assert.equal(res.body.success, true);
        assert.equal(res.body.message, 'Audio is downloading...');
        done();
      });
  });

  // Test for invalid YouTube URL
  it('should return an error for an invalid YouTube URL', function (done) {
    const invalidUrl = 'https://google.com';  // Invalid URL for testing

    request(app)
      .post('/download-audio')
      .send({ url: invalidUrl })
      .expect('Content-Type', /json/)
      .expect(200)
      .end((err, res) => {
        if (err) return done(err);
        
        // Assert the response contains an error message
        assert.equal(res.body.success, false);
        assert.equal(res.body.message, 'Invalid YouTube URL.');
        done();
      });
  });

  // Test for missing URL parameter
  it('should return an error if the URL is missing', function (done) {
    request(app)
      .post('/download-audio')
      .send({})
      .expect('Content-Type', /json/)
      .expect(200)
      .end((err, res) => {
        if (err) return done(err);
        
        // Assert the response contains an error message
        assert.equal(res.body.success, false);
        assert.equal(res.body.message, 'Invalid YouTube URL.');
        done();
      });
  });

  // Test for server error (e.g., if the download fails)
  it('should return an error if there is an issue with downloading audio', function (done) {
    const faultyUrl = 'https://www.youtube.com/watch?v=invalid';  // An invalid YouTube URL for testing error handling

    request(app)
      .post('/download-audio')
      .send({ url: faultyUrl })
      .expect('Content-Type', /json/)
      .expect(200)
      .end((err, res) => {
        if (err) return done(err);
        
        // Assert the response contains an error message
        assert.equal(res.body.success, false);
        assert.equal(res.body.message, 'Error downloading audio.');
        done();
      });
  });
});
