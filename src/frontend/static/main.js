$(document).ready(function() {
    // Load jobs
    loadJobs();
    loadIndexers();

    // Show Create Job Modal
    $('#createJobBtn').click(function() {
        $('#createJobModal').modal('show');
    });

    // Toggle between Manual and Auto fields based on job type selection
    $('#jobType').change(function() {
        if ($(this).val() === 'manual') {
            $('#manualFields').show();
            $('#autoFields').hide();
        } else {
            $('#manualFields').hide();
            $('#autoFields').show();
        }
    });

    // Toggle repeat options based on the checkbox
    $('#repeatCheck').change(function() {
        if ($(this).is(':checked')) {
            $('#repeatOptions').show();
        } else {
            $('#repeatOptions').hide();
        }
    });

    // Submit job
    $('#submitJob').click(function() {
        submitJob();
    });

    function loadJobs() {
    axios.get('/jobs', {
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        }
    })
    .then(function(response) {
        var jobsList = $('#jobsList');
        jobsList.empty(); // Clear current list
        response.data.forEach(function(job) {
            var jobElement = $(`
                <div class="card border-orange border-1">
                    <div class="card-body">
                        <div class="row">
                            <!-- Job Info and Actions -->
                            <div class="col-md-6">
                                <div class="card-header card-title">
                                    <h4 class="mb-0">Job Task: <em>${job.generatedCommand || job.command || ''}</em></h4>
                                </div>
                                <div class="card-text">
                                <span class="text-muted">Job ID: ${job._id} </span>
                                <p>
                                    Status: ${job.status}</div>
                                    Created: ${beforeNow(job.creationTimestamp)}
                                </p>
                                
                            </div>
                            <!-- Log Display -->
                            <div class="col-md-6">
                                <h4>Logs:</h4>
                                <div class="logs-container mt-3 p-3 card-hover" style="max-height: 200px; overflow-y: auto;">
                                    ${job.logs ? `<pre>${job.logs}</pre>` : '<pre>No logs available</pre>'}
                                </div>
                            </div>
                        </div>
                        <div class="card-actions mt-3">
                            <button class="btn btn-outline-danger delete-job" data-job-id="${job._id}">Delete</button>
                            <button class="btn btn-warning request-update ml-2" data-job-id="${job._id}">Update Logs</button>
                        </div>
                    </div>`);
                jobsList.append(jobElement);
            });
            completed = response.data.filter((x) => x.status == 'Completed')
            failed = response.data.filter((x) => x.status == 'Failed')
            console.log(completed, failed);
            console.log($('#totalCount'));
            console.log(response.data.length);
            document.getElementById('totalCount').innerHTML = response.data.length;
            document.getElementById('completedCount').innerHTML = completed.length;
            document.getElementById('failedCount').innerHTML = failed.length;

            attachDeleteEvent();
            attachRequestUpdateEvent(); 
        })
        .catch(function(error) {
            console.error("Error loading jobs:", error.response ? error.response.data : error);
            alert("Failed to load jobs. Check console for details.");
        });

    // Show Set Variables Modal
    $('#setVariablesBtn').click(function() {
        $('#setVariablesModal').modal('show');
        loadEnvironmentVariables();
    });

    // Update environment variables
    $('#updateVariables').click(function() {
        updateEnvironmentVariables();
    });

     // Update cronstrue output on Repeat Frequency input change
    $('#repeatFrequency').on('input', function() {
        var cronExpression = $(this).val();
        try {
        var readable = cronstrue.toString(cronExpression, { use24HourTimeFormat: true });
        $('#cronstrueOutput').text(readable).css('color', 'green');
        } catch (e) {
        $('#cronstrueOutput').text("Invalid cron expression").css('color', 'red');
        }
    });

}

function loadIndexers() {
    axios.get('/indexers' , {
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        }
    })
        .then(function(response) {
            var indexerList = $('#indexer-type-select');
            indexerList.empty(); // Clear current list
            response.data.forEach(function(indexer) {
                var indexerElement = $(`<option>${indexer.type}</option>`);
                indexerElement.val(indexer.type);
                indexerElement.data("indexer", indexer)
                indexerList.append(indexerElement);
            });
            attachDeleteEvent();
            attachRequestUpdateEvent(); 
        })
        .catch(function(error) {
            console.error("Error loading indexers:", error.response ? error.response.data : error);
            alert("Failed to load indexer. Check console for details.");
        });

}

function submitJob() {
    var jobType = $('#jobType').val();
    var command = $('#commandInput').val();
    var indexer = $('#indexer-type-select').find(':selected').data('indexer');
    var pipeline = $('#pipeline-type-select').find(':selected').val();
    var repeat = $('#repeatCheck').is(':checked');
    var repeatFrequency = $('#repeatFrequency').val();
    var record = $('#record-filter').val()

    console.log("Record: ", record)

    var envVarsText = $('#jobEnvVars').val();

    // Convert environment variables from text to an array of objects TODO code clone
    var envVars = envVarsText.split('\n').filter(line => line.trim() !== '').map(function(line) {
        var parts = line.split('=');
        return { name: parts[0].trim(), value: parts.slice(1).join('=').trim() };
    });

    // Construct job payload
    var payload = {environmentVariables: envVars};

    if (jobType == 'auto') {
        payload.indexerConfiguration = {
                    indexer: indexer,
                    record: record,
                    pipeline: pipeline
                }
    }
    else {
        payload.command = command;
    }

    // Add repeat information if applicable
    if (repeat) {
        // payload.repeat = repeat;
        payload.repeat = repeatFrequency;
    }

    axios.post('/jobs', payload, {
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        }
    })
    .then(function(response) {
        $('#createJobModal').modal('hide');
        loadJobs(); // Refresh job list
    })
    .catch(function(error) {
        console.error("Error submitting job:", error.response ? error.response.data : error);
        alert("Failed to submit job. Check console for details.");
    });
}

function attachDeleteEvent() {
    $('.delete-job').click(function() {
        var jobId = $(this).data('job-id');
        if (confirm('Are you sure you want to delete this job?')) {
            axios.delete('/jobs/' + jobId, {
                headers: {
                    'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
                }
            })
            .then(function(response) {
                loadJobs(); // Refresh the list of jobs
            })
            .catch(function(error) {
                console.error("Error deleting job:", error.response ? error.response.data : error);
                alert("Failed to delete job. Check console for details.");
            });
        }
    });
}

function attachRequestUpdateEvent() {
    $('.request-update').click(function() {
        var jobId = $(this).data('job-id');
        $(this).html(`<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...`).attr('disabled', true);
        requestLogsUpdate(jobId, $(this)); // Pass the button element for UI updates
    });
}

function requestLogsUpdate(jobId, buttonElement) {
    // Start the spinner
    buttonElement.html(`<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...`).attr('disabled', true);

    axios.post(`/jobs/${jobId}/request-logs-update`, {}, { 
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        }
    })
    .then(function(response) {
        // Wait for 5 seconds before fetching the updated job details
        setTimeout(function() {
            // Fetch updated job details
            axios.get(`/jobs/${jobId}`, {
                headers: {
                    'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
                }
            })
            .then(function(response) {
                // Update the job element with new logs
                updateJobElement(jobId, response.data);
                buttonElement.html('Update Logs').attr('disabled', false);
            })
            .catch(function(error) {
                console.error("Error fetching updated job details:", error.response ? error.response.data : error);
                alert("Failed to fetch updated job details. Check console for details.");
                buttonElement.html('Update Logs').attr('disabled', false);
            });
        }, 5000);
    })
    .catch(function(error) {
        console.error("Error requesting log update:", error.response ? error.response.data : error);
        alert("Failed to request log update. Check console for details.");
        buttonElement.html('Update Logs').attr('disabled', false);
    });
}

function updateJobElement(jobId, jobData) {
    // Find the job element by jobId or a unique identifier set for the job's card
    var jobElement = $(`[data-job-id="${jobId}"]`).closest('.card');
    // Update the logs container inside this job's card
    jobElement.find('.logs-container').html(jobData.logs ? `<pre>${encodeHTML(jobData.logs)}</pre>` : '<p>No logs available</p>');
}

function loadEnvironmentVariables() {
    axios.get('/environment_variables', {
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        }
    })
    .then(function(response) {
        // Assuming response.data is an array of objects with name and value
        var variablesText = response.data.map(varObj => `${varObj.name}=${varObj.value}`).join('\n');
        $('#variablesText').val(variablesText);
    })
    .catch(function(error) {
        console.error("Error loading environment variables:", error);
        alert("Failed to load environment variables. Check console for details.");
    });
}

function updateEnvironmentVariables() {
    var variablesArray = $('#variablesText').val().split('\n').map(function(line) {
        var [name, value] = line.split('=');
        return { name: name.trim(), value: value.trim() };
    });
    
    axios.post('/environment_variables', variablesArray, {
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        }
    })
    .then(function(response) {
        $('#setVariablesModal').modal('hide');
        alert("Environment variables updated successfully.");
    })
    .catch(function(error) {
        console.error("Error updating environment variables:", error);
        alert("Failed to update environment variables. Check console for details.");
    });
}

});

// Function to load environment variables into the job creation modal's textarea
function loadJobEnvVars() {
    axios.get('/environment_variables', {
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwtToken')
        }
    })
    .then(function(response) {
        var variablesText = response.data.map(varObj => `${varObj.name}=${varObj.value}`).join('\n');
        $('#jobEnvVars').val(variablesText);
    })
    .catch(function(error) {
        console.error("Error loading environment variables for job:", error);
        alert("Failed to load environment variables for job. Check console for details.");
    });
}

// Trigger loading of environment variables when the Create Job modal is shown
$('#createJobModal').on('shown.bs.modal', function () {
    loadJobEnvVars();
});

function encodeHTML(str){
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

