# Security Policy

## Reporting a Vulnerability

We take the security of our project seriously. If you believe you have found a security vulnerability, please report it to us as soon as possible.

**Do NOT open a public issue for security vulnerabilities.**

To report a vulnerability, please email us at [YOUR_EMAIL_ADDRESS]. Replace this with your actual email address where you wish to receive security reports. You can also report it directly through GitHub's built in vulnerability reporting system, by clicking `Security` -> `Advisories` -> `Report a Vulnerability`.

Please include the following information in your report:

- **Description of the vulnerability:** Provide a detailed explanation of the issue, including how it can be exploited.
- **Steps to reproduce:** Outline the specific steps required to reproduce the vulnerability.
- **Affected component(s):** Specify the part(s) of the project that are affected (e.g., `services/ai`, `services/frontend/src/components`).
- **Suggested mitigation (optional):** If you have any suggestions for how to fix the vulnerability, please include them.
- **Proof of concept (optional):** If possible, provide a proof of concept or exploit code to demonstrate the vulnerability. Please do not put sensitive information in the PoC.
- **Your contact information (optional):** If you would like to be credited for the discovery, please provide your name or preferred handle.

## Disclosure Process

Once we receive a vulnerability report, we will take the following steps:

1.  **Acknowledge receipt:** We will acknowledge receipt of your report within 3 business days.
2.  **Investigate and verify:** Our security team will investigate the report and attempt to verify the vulnerability.
3.  **Develop a fix:** If the vulnerability is confirmed, we will develop a fix as soon as possible.
4.  **Release the fix:** We will release the fix in a new version of the project.
5.  **Public disclosure:** We will publicly disclose the vulnerability after the fix has been released. We will credit you for the discovery unless you wish to remain anonymous.

## Scope

This security policy applies to all components of the project, including:

- **`services/ai`:** This component contains the backend AI service with FastAPI, including Python code, test suites, and related configuration.
- **`services/frontend`:** This component contains the React-based frontend user interface, including TypeScript/JavaScript, CSS, and static assets.
- **`services/webui_legacy`:** This component contains the deprecated HTML/JavaScript frontend (to be removed).
- **`docs`:** This directory contains documentation for the project.
- **`scripts`:** This directory contains utility scripts.
- Any other code, configuration, or data within this repository.

## Out of Scope

The following are considered out of scope for this security policy:

- Vulnerabilities in third-party dependencies that are not directly caused by our code. We encourage you to report these vulnerabilities to the maintainers of the respective dependencies.
- Vulnerabilities that require physical access to the server or infrastructure.
- Social engineering attacks against project contributors or users.
- Denial of service attacks.
- Reports that do not demonstrate a security impact.
- Issues that are already publicly known.

## Security Best Practices

We strive to follow security best practices in the development and maintenance of this project. These include:

- **Regular code reviews:** We perform code reviews to identify potential security issues before they are merged into the main branch.
- **Dependency management:** We regularly update dependencies to patch known vulnerabilities.
- **Secure coding practices:** We follow secure coding guidelines to prevent common vulnerabilities.
- **Input validation:** We validate all user inputs to prevent injection attacks.
- **Output encoding:** We properly encode output to prevent cross-site scripting (XSS) attacks.
- **Authentication and authorization:** We implement appropriate authentication and authorization mechanisms to protect sensitive data and functionality.
- **Least privilege:** We follow the principle of least privilege, granting users and processes only the necessary permissions.

## Responsible Disclosure

We appreciate researchers who follow responsible disclosure principles. This means:

- Giving us reasonable time to fix the vulnerability before publicly disclosing it.
- Avoiding actions that could harm users or disrupt the service.
- Not exploiting the vulnerability for personal gain or malicious purposes.

## Bug Bounty Program

Currently, we do not offer a bug bounty program. However, we greatly appreciate the efforts of security researchers who report vulnerabilities to us, and we may offer rewards or recognition on a case-by-case basis in the future.

## Contact

If you have any questions or concerns about this security policy, please contact us at [YOUR_EMAIL_ADDRESS].

**Thank you for helping us keep our project secure!**
