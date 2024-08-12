# Bertha Web Crawler  🚀

Welcome to **Bertha Web Crawler**! This project is a powerful yet simple tool designed to help you discover and index all pages of a website. Whether you're building a search engine, monitoring a site for changes, or simply exploring the web, Bertha provides the functionality you need to efficiently crawl web pages, track their status, and manage the data in a structured way using SQLite.

With **Bertha**, you can easily initiate a full crawl of a website, perform selective recrawls based on time intervals, and even focus on specific pages. The package is built to be flexible and easy to use, making it suitable for both small projects and larger web crawling tasks.


## Features ✨

- **Crawl Entire Websites**: Easily crawl a website to discover all pages, storing URLs and metadata in a SQLite database. 🎉
- **Selective Recrawl**: Recrawl specific pages or the entire website, either based on a time gap or by forcing a recrawl of all pages. 🔥
- **HTTP Status Tracking**: Track the HTTP status of each page, ensuring that only available pages are stored and processed. 🌟


## Installation 💻

You can install the package via pip:

```bash
pip install GIT+https://github.com/alexruco/bertha

```
## Usage 📚

Here's a quick example to get you started:

```python
from bertha import crawl_website, recrawl_website, recrawl_url


# Crawl a website with the default gap of 30 days
crawl_website("https://www.example.com")

# Force a recrawl of the entire website
recrawl_website("https://www.example.com")

# Recrawl a specific URL
recrawl_url("https://www.example.com/specific-page")
```
-->
Documentation 📖

Documentation is available at [link to documentation].
Running Tests 🧪

To run the tests, you can use the unittest module or pytest.

bash

python -m unittest discover tests
# or
pytest

## Contributing 🤝

We welcome contributions from the community! Here’s how you can get involved:

1. **Report Bugs**: If you find a bug, please open an issue [here](https://github.com/alexruco/bertha/issues).
2. **Suggest Features**: We’d love to hear your ideas! Suggest new features by opening an issue.
3. **Submit Pull Requests**: Ready to contribute? Fork the repo, make your changes, and submit a pull request. Please ensure your code follows our coding standards and is well-documented.
4. **Improve Documentation**: Help us improve our documentation. Feel free to make edits or add new content.

### How to Submit a Pull Request

1. Fork the repository.
2. Create a new branch: `git checkout -b my-feature-branch`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin my-feature-branch`.
5. Open a pull request on the original repository.

## License 📄

This project is licensed under the MIT License. Feel free to use, modify, and distribute this software in accordance with the terms outlined in the [LICENSE](LICENSE) file.

## Name Inspiration 🌸

The name **Bertha** is chosen in honor of **Bertha Lutz**, a prominent Brazilian zoologist (specializing in amphibians), politician, diplomat, and a pioneering leader in the feminist and human rights movements across the Americas. 

Bertha Lutz's legacy is one of resilience, determination, and advocacy for equality. She played a critical role in advancing women's rights, not only in Brazil but also on the international stage. Her work and influence were instrumental in the formation of the United Nations Commission on the Status of Women. 

