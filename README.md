# 

```
 _________  _______          _        ______  ________  
|  _   _  ||_   __ \        / \     .' ___  ||_   __  | 
|_/ | | \_|  | |__) |      / _ \   / .'   \_|  | |_ \_| 
    | |      |  __ /      / ___ \  | |         |  _| _  
   _| |_    _| |  \ \_  _/ /   \ \_\ `.___.'\ _| |__/ | 
  |_____|  |____| |___||____| |____|`.____ .'|________| 
                                                        

```

<!-- PROJECT SHIELDS -->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Branches][branches-shield]][branches-url]
[![Issues][issues-shield]][issues-url]
[![Unlicense License][license-shield]][license-url]





<!-- PROJECT LOGO -->
<br />

<div align="center">
  <!-- <a href="">
    <img src="images/logo.png" alt="Logo" width="80" height="80"> -->
  
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#running-the-program">Running the Program </a></li>
        <li><a href="#sveltekit">SvelteKit</a></li>
      </ul>
    </li>
    <li><a href="#bruteforcer">Bruteforcer</a></li>
    <li><a href="#crawler">Crawler</a></li>
    <li><a href="#ai-tool">AI-Tools</a></li>
    <li><a href="#contributors">Contributors</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

The TRACE system is a penetration testing toolkit that supports cybersecurity and is employed by the Data Analysis Center's Cyber Experimentation & Analysis Division (DAC CEAD) to assist analysts in examining vulnerabilities within applications and networks. The system is designed to automate reconnaissance and exploitation operations to enhance the process. The system uses artificial intelligence (AI) to create credentials, data from enterprise testing tools to create more effective username and password lists. TRACE can be used by analysts to scan IP addresses, monitor scan progress, and export results in an organized format.

TRACE is developed to support DoD penetration testing with efficient testing for security against major technological systems. As the biggest concern for DoD operations would be security and resiliency, analysts carrying out this with the help of TRACE will be able to identify bugs, carry out brute-force attacks programmatically, initiate SQL injections, and generate solid security reports. The software is not meant to perform penetration testing on its own but provides a formal environment to assist in carrying out various security assessment activities. TRACE focuses on optimizing test effectiveness by automating the execution of procedures that can otherwise be done manually, such as directory brute force, HTTP request modification, and wordlist generation using AI.

The system provides a suite of penetration testing tools such as project management, network discovery, AI-driven credential cracking, and visualization tools. The analysts are able to import projects, set up services, choose particular machines to test, and display real-time security scan progress.TRACE enables the utilization of shallow learning AI algorithms to derive meaningful patterns from data, maximizing brute-force attempts by creating highly likely username-password combinations. In addition, the system provides structured results in tree graph structures, enabling users to navigate found vulnerabilities more effectively.

TRACE is installed for use by two primary roles: Lead Analysts and Analysts. The administrative role is owned by the Lead Analyst, which involves creating, deleting, and locking projects, while Analysts can perform scans, modify requests, and analyze results. The system is web-based, and access is guaranteed by stringent security measures. TRACE uses no third-party internet access but operates in an internal network that is secured on the basis of secure communication channels such as SSL/TLS for HTTPS and also encrypted data channels.


<p align="right">(<a href="#">back to top</a>)</p>



### Built With

The TRACE backend is developed using Python 3.14, and the frontend is developed using SvelteKit v2.16.1. The database system uses Neo4j 5.26.1 for network mapping and storing penetration test data. The system operates on computers with at least 8GB RAM, a 4-core 2.5 GHz processor, and 10GB of free storage. TRACE does not use Docker for deployment, instead opting for a more traditional software installation process. Targeted Operating System is Kali Linux.

* [![Svelte][Svelte.dev]][Svelte-url]
* [![JavaScript.com]][JavaScript-url]
* [![HTML][HTML.com]][HTML-url]
* [![Neo4j][Neo4j.com]][Neo4j-url]
* [![Python][Python.com]][Python-url]

<p align="right">(<a href="#">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites


* npm
  ```sh
  npm install npm@latest -g
  
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/dgome547/TRACE
   ```
2. Install NPM packages
   ```sh
   npm init vite@latest .
   npm install

   ```
3. Install necessary dependencies.
   ```sh
   cd backend 
   pip install -r requirements.txt
   ```

## Running the Program 
1. Start Neo4j (skip for now will generate errors but will still run)
2. Start backend via FastAPI
```bash
    cd /backend
    uvicorn app.main:app --reload --host 127.0.0.1 --port 5000
```
3.  Start SvelteKit (Frontend)
``` bash 
cd /frontend
npm run dev -- --open
```

## NOTE:
*   The .gitignore is setup to ignore the files to which are created by your system specifically for your system. If it is changed than a file may cause issues for other to pull the code from the repo. Which is why you must setup the environment with the above steps for the first time.


## SvelteKit

![image](/TRACE-assets/R123.png)

SvelteKit can be viewed as a client server structure it uses +page.svelte for client-side components and +page.server.ts for server-side data fetching. +layout.svelte defines shared UI, while +layout.server.ts fetches data for all nested routes. The basic file structure of the .svelte file contains JS, CSS, and HTML within the same document as seen below. 
<strong> NOTE </strong> the svelte framework is poorly written in terms of this architecture however is just the baseline to show how the backend ties to the frontend.


  ```svelte
  <script> 
    /* JS */
  </script>

  <style>
    /* CSS */
  </style>

  <!-- HTLML -->
  ```

## File Structure 
TRACE is built with a modular structure, with the same a similar client server structure this is referred to as the front and back ends. The backend is often treated as the server hence why it is important to setup the backend first and than the frontend. Here is a current working of the project directory.


                               SvelteKit Structure




```
trace-project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app entry
│   │   ├── state.py                 # Shared crawler config (active_config)
│   │   ├── crawler/
│   │   │   ├── __init__.py
│   │   │   ├── crawler.py     #Crawler engine
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py          #General Routes 
│   │   │   ├── crawler_routes.py  #WebSocket+Routes
│   ├── crawl_results.csv            # Output CSV 
│
├── frontend/
│   ├── src/
│   │   ├── routes/
│   │   │   ├── +layout.svelte       # Sidebar and overall layout
│   │   │   ├── +page.svelte         # Landing or base redirect page
│   │   │   ├── crawler/
│   │   │   │   ├── launch/+page.svelte     # Crawler config form (start)
│   │   │   │   ├── execution/+page.svelte  # Real-time crawler status (WebSocket)
│   │   │   │   ├── results/+page.svelte    # Final results (CSV display)
│   ├── static/                      # Static assets (optional)
│   ├── package.json
│   ├── vite.config.js
│   ├── svelte.config.js
│   └── tsconfig.json (if TypeScript)
│
├── .env                             # Backend credentials (e.g. Neo4j, if needed)
├── requirements.txt                 # Python dependencies
├── README.md

```
<p align="right">(<a href="#">back to top</a>)</p>


<!-- Bruteforcer -->
## Bruteforcer

TRACE system Brute Forcer is a penetration tool that tries to identify concealed directories and files in a target web application by brute-forcing HTTP requests against pre-set wordlists.Analysts can configure parameters such as target URL, top-level directory, response filtering, and wordlist to adjust the brute-force attack.The utility traverses probable paths, analyzing server responses to determine what directories or files exist. It is paired with the Crawler for high accuracy and with the AI module to generate optimized wordlists for credential attacks. The output is formatted in a structured way, so that analysts can instantly identify unsecured assets, misconfigurations, or potential entry points in the system.

<p align="right">(<a href="#">back to top</a>)</p>



<!-- Crawler -->
## Crawler
The TRACE system's Crawler methodically maps and uncovers the structure of a target web application by discovering web pages, directories, and resources available. It does this by sending HTTP requests to a target URL, parsing the responses, and identifying links to further follow into the site structure. The application supports multiple adjustments such as crawl depths, request timing, and proxy settings are some of the scanning settings available to the analysts to modify the scan process.This output is used to build a hierarchical tree structure  to model the web application  and to assist with penetration testing by identifying weaknesses of attack surfaces. It is also handed over to the AI module for keyword and pattern identification to assist in generating useful wordlists for subsequent tests.


<p align="right">(<a href="#">back to top</a>)</p>




<!-- AI-Tool -->
## AI-Tool

TRACE integrates NLP and artificial intelligence algorithms to make penetration testing more effective. The AI part has been coded to maximize brute-force attacks, optimize username-password guessing, and improve learning patterns from previous testing outcomes. Additionally, the NLP component trims and collects meaningful information from websites scanned, removing redundant keywords and concentrating on key details. All these help to enable TRACE to generate highly effective attack methods specifically for attacking specific targets.

<p align="right">(<a href="#">back to top</a>)</p>


### Intro to Svelte and Frontend Structure



<p align="right">(<a href="#">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributors
<a href="https://github.com/dgome547/TRACE/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=dgome547/TRACE" alt="contrib.rocks image" />
</a>


<p align="right">(<a href="#">back to top</a>)</p>


<!-- LICENSE -->
## License

License not specified 

<p align="right">(<a href="#">back to top</a>)</p>





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->


[contributors-shield]:https://img.shields.io/github/contributors/dgome547/TRACE.svg?style=for-the-badge
[contributors-url]: https://github.com/dgome547/TRACE/graphs/contributors

[forks-shield]: https://img.shields.io/github/forks/dgome547/TRACE.svg?style=for-the-badge
[forks-url]: https://github.com/dgome547/TRACE/forks

[branches-shield]: https://img.shields.io/badge/Branches-4-green?style=for-the-badge
[branches-url]: https://github.com/dgome547/TRACE/branches

[issues-shield]: https://img.shields.io/github/issues/dgome547/TRACE.svg?style=for-the-badge
[issues-url]: https://github.com/dgome547/TRACE/issues 

[license-shield]: https://img.shields.io/github/license/dgome547/TRACE.svg?style=for-the-badge
[license-url]: https://github.com/dgome547/TRACE/blob/master/LICENSE.txt

[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/

[JavaScript.com]: https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black&style=for-the-badge
[JavaScript-url]: https://www.javascript.com/

[HTML.com]: https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white&style=for-the-badge
[HTML-url]: https://html.com

[Neo4j.com]:https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white
[Neo4j-url]: https://neo4j.com

[Python.com]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org