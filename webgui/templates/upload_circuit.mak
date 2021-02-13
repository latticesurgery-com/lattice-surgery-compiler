<!DOCTYPE html>
<html lang="en">
<head>
<title>Lattice Surgery Compiler</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* {
  box-sizing: border-box;
}

body {
  font-family: Arial, Helvetica, sans-serif;
}

/* Style the header */
header {
  background-color: #666;
  padding: 10px;
  text-align: center;
  font-size: 15px;
  color: white;
}

/* Create two columns/boxes that floats next to each other */
nav {
    float: left;
    width: 20%;
    background: #ccc;
    padding: 20px;
    height: 100%;
}

/* Style the list inside the menu */
nav ul {
  list-style-type: none;
  padding: 0;
}

article {
    float: left;
    padding: 20px;
    width: 80%;
    background-color: #f1f1f1;
    font-size: 10pt;
}

/* Clear floats after the columns */
section::after {
  content: "";
  display: table;
  clear: both;
}

/* Style the footer */
footer {
  background-color: #777;
  padding: 10px;
  text-align: center;
  color: white;
}

/* Responsive layout - makes the two columns/boxes stack on top of each other instead of next to each other, on small screens */
@media (max-width: 600px) {
  nav, article {
    width: 100%;
    height: auto;
  }
}
</style>
</head>
<body>

<header>
  <h2>Quantum Error Correction Compiler with Lattice Surgery</h2>
</header>

<section>
  <nav>
    <ul>
      <li><a href="#">Compile Quantum Circuit</a></li>
    </ul>
  </nav>

  <article>
    <h2>Get Started</h2>
      <p>Upload a quantum circuit. <a>What is supported</a>.
        <form action="${request.route_path('lattice_view')}" method="post" accept-charset="utf-8"
          enctype="multipart/form-data">
            <input id="circuit" name="circuit" type="file" value="" />
            <input type="submit" value="Go!" />
        </form>

      </p>
    <h1>About</h1>
    <p>
        A proposed solution to mitigate the occurrence of errors in quantum computers are the so-called quantum error correcting codes (QECC). Specifically we focus on the protocol of <strong>lattice surgery</strong>, which is based on the prominent methodology of <strong>surface codes</strong>. A natural question relates to how these techniques can be employed to systematically obtain fault tolerant logical qubits from less reliable ones. Recent work has focused on building compilers that translate a logical quantum circuit to a much larger error corrected one, with the output circuit performing the computation specified by the logical circuit with QECCs [1][2].
    </p>
    <p>
        <img src="/static/lattice_view_example.png" style="width: 100%">
    </p>
    <p>
        Surface codes are a family of QECCs that aims at improving computation fidelity by entangling many quantum mechanical entities in a two dimensional lattice. Our technique of choice for operating on this lattice is a protocol known as lattice surgery, which stores logical qubits in portions of the surface code's lattice patches and performs logical operations by merging and splitting patches [3].
    </p>
    <p>
        This program handles a portion of the logical to physical compilation. It takes a quantum circuit and translates it to a representation of lattice surgery operations, which are in direct correspondence with the physical error corrected circuit, up to code distance. The project comes with a visualizer tool (figure), that shows the state of the surface code lattice state in between surgery operations.
    </p>

  </article>
</section>

<footer>
  <p>Contact &nbsp; | &nbsp; Github &nbsp; | &nbsp; Paper</p>
</footer>

</body>
</html>
