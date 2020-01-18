
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="Mark Otto, Jacob Thornton, and Bootstrap contributors">
    <meta name="generator" content="Jekyll v3.8.6">
    <title>Manage Hiring Process - Hirenator</title>

    <link rel="canonical" href="https://getbootstrap.com/docs/4.4/examples/offcanvas/">

    <link rel="stylesheet"
       href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
       integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh"
       crossorigin="anonymous"
    >

    <!-- Favicons -->
    <link rel="apple-touch-icon" href="/docs/4.4/assets/img/favicons/apple-touch-icon.png" sizes="180x180">
    <link rel="icon" href="/docs/4.4/assets/img/favicons/favicon-32x32.png" sizes="32x32" type="image/png">
    <link rel="icon" href="/docs/4.4/assets/img/favicons/favicon-16x16.png" sizes="16x16" type="image/png">
    <link rel="manifest" href="/docs/4.4/assets/img/favicons/manifest.json">
    <link rel="mask-icon" href="/docs/4.4/assets/img/favicons/safari-pinned-tab.svg" color="#563d7c">
    <link rel="icon" href="/docs/4.4/assets/img/favicons/favicon.ico">
    <meta name="msapplication-config" content="/docs/4.4/assets/img/favicons/browserconfig.xml">
    <meta name="theme-color" content="#563d7c">


    <style>
      .bd-placeholder-img {
        font-size: 1.125rem;
        text-anchor: middle;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
      }

      @media (min-width: 768px) {
        .bd-placeholder-img-lg {
          font-size: 3.5rem;
        }
      }
    </style>
    <!-- Custom styles for this template -->
    <link href="offcanvas.css" rel="stylesheet">
  </head>
  
  <body class="bg-light">
    <main role="main" class="container">
      <div class="d-flex align-items-center p-3 my-3 text-white-50 bg-purple rounded shadow-sm bg-primary">
        <!--img class="mr-3" src="/docs/4.4/assets/brand/bootstrap-outline.svg" alt="" width="48" height="48"-->
        <div class="lh-100 ">
          <h6 class="mb-0 text-white lh-100">Hirenator</h6>
        <small>The AI is here!</small>
        </div>
      </div>

      <!-- JUMBOTRON -->
      <!--div class="jumbotron jumbotron-fluid">
        <div class="container">
          <h1 class="display-4">Name of the position #ID</h1>
          <p class="lead">
            Brief description of the hiring process. 
          </p>
        </div>   
      </div-->
      <!-- END JUMBOTRON -->

      <div class="row mb-2">
        <div class="col-md-12">
          <div class="row no-gutters border rounded overflow-hidden flex-md-row mb-4 shadow-sm h-md-250 position-relative">
            <div class="col p-4 d-flex flex-column position-static">
              <strong class="d-inline-block mb-2 text-primary">On time</strong>
              <h3 class="mb-0">Name of the position #ID</h3>
              <div class="mb-1 text-muted">Due date: ##DATE</div>
              <p class="card-text mb-auto">Brief description of the project.</p>
              <a href="manage_process.php" class="stretched-link">Manage hiring process</a>
            </div>
            <div class="col-auto d-none d-lg-block">
              <svg 
                class="bd-placeholder-img" width="200" height="250"
                 xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice"
                 focusable="false" role="img" aria-label="Placeholder: Thumbnail"
              >
                <title>Placeholder</title>
                <rect width="100%" height="100%" fill="#55595c"></rect>
                <text x="50%" y="50%" fill="#eceeef" dy=".3em">Progress</text>
              </svg>
            </div>
          </div>
        </div>
        <div class="col-md-12">
          <div class="row no-gutters border rounded overflow-hidden flex-md-row mb-4 shadow-sm h-md-250 position-relative">
            <div class="col p-4 d-flex flex-column position-static">
              <strong class="d-inline-block mb-2 text-primary">On time</strong>
              <h3 class="mb-0">Name of the position #ID</h3>
              <div class="mb-1 text-muted">Due date: ##DATE</div>
              <p class="card-text mb-auto">Brief description of the project.</p>
              <a href="manage_process.php" class="stretched-link">Manage hiring process</a>
            </div>
            <div class="col-auto d-none d-lg-block">
              <svg 
                class="bd-placeholder-img" width="200" height="250"
                 xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice"
                 focusable="false" role="img" aria-label="Placeholder: Thumbnail"
              >
                <title>Placeholder</title>
                <rect width="100%" height="100%" fill="#55595c"></rect>
                <text x="50%" y="50%" fill="#eceeef" dy=".3em">Progress</text>
              </svg>
            </div>
          </div>
        </div>
      </div>    
      <div class=col-md-12">
        <button type="button" class="btn btn-primary float-left" data-toggle="modal" data-target="#new-hiring">
          <i class="fas fa-plus-square"></i>
          New Process
        </button>
      </div>
    </main>

    <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.4.1.slim.min.js" integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>

    <script src="https://kit.fontawesome.com/6bcd798364.js" crossorigin="anonymous"></script>

    <!-- MODAL NEW QUESTION -->
    <div class="modal fade" id="new-hiring" tabindex="-1" role="dialog" aria-labelledby="new-process-modal-hiring-title" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="new-hiring-title">Add new hiring process</h5>
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <form>
              <div class="form-group row">
                <label for="colFormLabel" class="col-sm-3 col-form-label">Position Title</label>
                <div class="col-sm-9">
                  <input class="form-control" id="colFormLabel" placeholder="Software Engineer">
                </div>
              </div>
              <div class="form-group row">
                <label for="colFormLabel" class="col-sm-3 col-form-label">Descriptionn</label>
                <div class="col-sm-9">
                  <textarea class="form-control" id="colFormLabel" placeholder="?"></textarea>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary">Save changes</button>
          </div>
        </div>
      </div>
    </div>
    <!-- END MODAL NEW CANDIDATE -->


  </body>
</html>

