# NotesGen AWS Deployment Setup

## 🔐 Security-First AWS Infrastructure Setup

This directory contains security-hardened AWS IAM policies and setup scripts for deploying the NotesGen application following AWS Well-Architected Framework security best practices.

---

## 📁 Files Overview

```
aws-setup/
├── README.md                                    # This file
├── AWS-SECURITY-CHECKLIST.md                   # Comprehensive security checklist
├── setup-iam-secure.sh                         # Main setup script (RECOMMENDED)
├── setup-iam.sh                               # Legacy script (NOT RECOMMENDED)
├── notesgen-deployment-policy-secure.json      # Secure deployment policy
├── notesgen-ec2-role-policy-secure.json       # Secure EC2 runtime policy
├── ec2-trust-policy.json                      # EC2 trust policy
├── notesgen-deployment-policy.json            # Legacy broad policy (NOT RECOMMENDED)
└── notesgen-ec2-role-policy.json             # Legacy broad policy (NOT RECOMMENDED)
```

---

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI v2** installed and configured
2. **jq** installed for JSON processing
3. **Administrative IAM permissions** in your AWS account
4. **Terminal access** with bash

### Installation Check

```bash
# Check AWS CLI
aws --version

# Check jq
jq --version

# Verify AWS credentials
aws sts get-caller-identity
```

### Run the Setup

```bash
# Navigate to aws-setup directory
cd aws-setup

# Make script executable (if not already)
chmod +x setup-iam-secure.sh

# Run the secure setup script
./setup-iam-secure.sh
```

---

## 🔒 Security Features

### Principle of Least Privilege
- **Scoped permissions**: Only NotesGen-specific resources
- **Regional restrictions**: Limited to us-east-1 and us-west-2
- **Resource-based access**: S3 buckets, IAM roles, SSM parameters scoped to `notesgen-*`

### Encryption Requirements
- **S3**: Server-side encryption (AES256) enforced
- **RDS**: Encryption at rest required
- **SSM**: SecureString parameters for sensitive data
- **KMS**: Controlled key access via service conditions

### Conditional Access Controls
- **Service-based restrictions**: KMS access only via specific AWS services
- **Tag-based conditions**: Resource access based on proper tagging
- **Action-based conditions**: Limited creation actions for security groups

---

## 📋 What the Script Creates

### IAM User: `notesgen-deploy-user`
- **Purpose**: Deployment and infrastructure management
- **Permissions**: Secure deployment policy with minimal required access
- **Tags**: Project, Environment, Purpose, CreatedBy, CreatedDate

### IAM Role: `NotesGen-EC2-Role`
- **Purpose**: Runtime permissions for EC2 instances
- **Permissions**: Application-specific access to S3, CloudWatch, SSM
- **Trust Policy**: Allows EC2 instances to assume the role

### IAM Policies
1. **NotesGen-Deployment-Policy**: For infrastructure deployment
2. **NotesGen-EC2-Runtime-Policy**: For application runtime

### Instance Profile
- **NotesGen-EC2-Role-InstanceProfile**: Links the role to EC2 instances

---

## 🔑 Credentials Management

### Access Keys
The script creates access keys for the deployment user and saves them to:
```
aws-credentials-notesgen-deploy-user.txt
```

**⚠️ SECURITY WARNING**: 
- Store these credentials securely in your CI/CD system
- Delete the credentials file after copying
- Rotate keys regularly (script prompts for rotation)

### For GitHub Actions
Add these as repository secrets:
```
AWS_ACCESS_KEY_ID: [from credentials file]
AWS_SECRET_ACCESS_KEY: [from credentials file]
AWS_DEFAULT_REGION: us-east-1
```

---

## 🛠️ Configuration Options

### Environment Variables
```bash
# Set environment (default: dev)
export ENVIRONMENT=production

# Set AWS region (default: us-east-1)
export AWS_REGION=us-west-2

# Run setup
./setup-iam-secure.sh
```

### Supported Environments
- `dev` (development)
- `staging` 
- `prod` (production)

---

## 🔍 Verification

### Check User Creation
```bash
aws iam get-user --user-name notesgen-deploy-user
```

### Check Role Creation
```bash
aws iam get-role --role-name NotesGen-EC2-Role
```

### Check Policy Attachment
```bash
aws iam list-attached-user-policies --user-name notesgen-deploy-user
aws iam list-attached-role-policies --role-name NotesGen-EC2-Role
```

### Test Permissions
```bash
# Switch to deployment user credentials
export AWS_ACCESS_KEY_ID=[from credentials file]
export AWS_SECRET_ACCESS_KEY=[from credentials file]

# Test S3 access (should work)
aws s3 ls

# Test broader permissions (should fail)
aws iam list-users
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Insufficient Permissions
```
Error: User is not authorized to perform: iam:CreateUser
```
**Solution**: Ensure your current AWS user has IAM administrative permissions.

#### 2. User Already Exists
```
User notesgen-deploy-user already exists
```
**Solution**: The script will prompt to update the existing user. Choose 'y' to proceed.

#### 3. Policy Version Limit
```
Cannot exceed quota for PolicyVersionsPerPolicy
```
**Solution**: Delete old policy versions or contact AWS support for quota increase.

#### 4. Missing jq
```
Command 'jq' not found
```
**Solution**: Install jq:
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# CentOS/RHEL
sudo yum install jq
```

### Debug Mode
Run with debug output:
```bash
bash -x setup-iam-secure.sh
```

---

## 🔄 Updates and Maintenance

### Policy Updates
When policies need updates:
1. Modify the JSON policy files
2. Re-run `./setup-iam-secure.sh`
3. Script will create new policy versions automatically

### Access Key Rotation
```bash
# List existing keys
aws iam list-access-keys --user-name notesgen-deploy-user

# Create new key (script prompts for this)
./setup-iam-secure.sh

# Update CI/CD systems with new keys

# Delete old key
aws iam delete-access-key --user-name notesgen-deploy-user --access-key-id [OLD_KEY_ID]
```

### Cleanup
To remove all created resources:
```bash
# WARNING: This will delete all NotesGen IAM resources
./cleanup-iam.sh  # (if created)
```

---

## 📚 Security Best Practices

### Do's ✅
- ✅ Use the secure setup script
- ✅ Rotate access keys regularly
- ✅ Store credentials securely
- ✅ Use environment-specific deployments
- ✅ Enable CloudTrail logging
- ✅ Regular security reviews

### Don'ts ❌
- ❌ Use the legacy broad policies
- ❌ Store credentials in code
- ❌ Use root account for deployment
- ❌ Grant unnecessary permissions
- ❌ Skip security monitoring

---

## 🤝 Support

### Documentation
- [AWS-SECURITY-CHECKLIST.md](./AWS-SECURITY-CHECKLIST.md)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/)

### Help
If you encounter issues:
1. Check the troubleshooting section above
2. Review the AWS CloudTrail logs
3. Consult the AWS documentation
4. Contact your AWS support team

---

**Last Updated**: December 2024
**Security Review**: Monthly
**Next Review**: January 2025 