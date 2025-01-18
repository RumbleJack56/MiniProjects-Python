const { scholarly } = require('scholarly');

exports.handler = async (event) => {
  try {
    const authorName = "Dinesh K. Vishwakarma"; // Change this as needed
    const searchResults = await scholarly.search(authorName);
    const author = searchResults[0]; // Get the first result

    // Fetch detailed metrics
    const details = await scholarly.getMetrics(author.url);

    return {
      statusCode: 200,
      body: JSON.stringify({
        name: details.name,
        affiliation: details.affiliation,
        url_picture: details.photo,
        citedby: details.citedBy,
        citedby5y: details.citedBy5y,
        hindex: details.hIndex,
        hindex5y: details.hIndex5y,
        i10index: details.i10Index,
        i10index5y: details.i10Index5y,
        cites_per_year: details.citesPerYear,
      }),
    };
  } catch (error) {
    console.error("Error fetching data:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Unable to fetch data" }),
    };
  }
};
