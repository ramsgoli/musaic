const express = require('express')
const router = express.Router()

router.use('/upload', require('./upload'))
router.use('/auth', require('./auth'))

module.exports = router
