const aws = require('aws')
const express = require('express')
const config = require('../../../config')

const router = express.Router()

class Upload {
  static async signS3(req, res, next) {
    const s3 = new aws.s3()
    const fileName = req.query['file-name']
    const fileType = req.query['file-type']
    const s3Params = {
      Bucket: config.s3Bucket,
      Key: fileName,
      ContentType: fileType,
      ACL: 'public-read'
    }

    s3.getSignedUrl('putObject', s3Params, (err, data) => {
      if (err) {
        return next(err)
      }

      const returnData = {
        signedRequest: data,
        url: `https://${config.s3Bucket}.s3.amazonaws.com/uploads/{fileName}`
      }
      res.write(JSON.stringify(returnData))
      res.end()
    })
  }
}

router.get('/sign-s3', Upload.signS3)

module.exports = router
