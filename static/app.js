g_ctx = {
    "topic_count":0,
    "sess_label":null,
    "subject":null,
    "fact_flag":false,
    "post_flag":false,
    "check_id":null,
    "post_id":null,
}

g_check_id=null;

function get_ele( id )
{
    ele = document.getElementById(id);
    if( ele == null )
    {
	console.log("ele id:"+id+" is not valid.")
    }
    return ele
}

function create_ele( ele_type )
{
    return document.createElement(ele_type)
}

function set_status( msg )
{
    get_ele('status_text_id').innerHTML = msg;    
}


function on_check(ele_id)
{
    var ele_is_checked = get_ele(ele_id).checked
    
    if( ele_is_checked && ele_id != g_ctx.check_id  )
    {
	if(g_ctx.check_id != null)
	    get_ele(g_ctx.check_id).checked = false;
	g_ctx.check_id = ele_id;
	g_ctx.post_id  = get_ele(ele_id).post_id;
    }

    if( !ele_is_checked && ele_id == g_ctx.check_id )
    {
	g_ctx.check_id = null;
	g_ctx.post_id = null;
    }
}


function submit_form( endpoint, formData )
{
    return fetch('http://127.0.0.1:5000/'+endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
        .then(response => response.json())
        .then(data => {
	    return data;
        })
        .catch((error) => {
            console.error('Error:', error);
	    throw error;
        });

    set_status( "Processing ..." )
}

function create_para_ele( title, parentEle, text )
{
    var div_ele = create_ele("div");
    div_ele.className = "para_div";  
    
    var title_ele = create_ele("p");
    title_ele.className = "para_title";
    title_ele.innerHTML = title;
    div_ele.appendChild(title_ele)
    
    var text_ele = create_ele("p");
    text_ele.className = "para_text";    
    text_ele.innerHTML = text;  
    div_ele.appendChild(text_ele);
    
    parentEle.appendChild(div_ele)
}

function update_topic_list( r )
{
    var topicListDiv = get_ele("topic_list_div")
    
    let i = 0;
    for(i=0; i<r['topicL'].length; ++i)
    {
	var t = r['topicL'][i];
	
	var div = create_ele("div");
	div.className="topic_div"

	create_para_ele("Title:",div,t.title)
	create_para_ele("Description:",div,t.description)
	
	topicListDiv.appendChild(div)	    
    }	
}

function submit_topic_gen_form()
{
    const formData = {
	sess_label:   get_ele('sess_label_id').value,
        sess_subject: get_ele('sess_subject_id').value,
	topic_count:  get_ele('topic_count_id').value,
    };

    console.log("Removing lists")
    
    // remove topic-list
    var topicListDiv = get_ele("topic_list_div")
    topicListDiv.replaceChildren();
    
    // remove the fact-list
    var factListDiv = get_ele("facts_list_div")
    factListDiv.replaceChildren();

    // remove post-list
    var postListDiv = get_ele("post_list_div")
    postListDiv.replaceChildren();

    // hide buttons
    get_ele('facts_div').style.display = 'none';
    get_ele('posts_div').style.display = 'none';
    get_ele('publish_div').style.display = 'none';
    
    
    
    submit_form("gen_topics",formData).then((r) => {
	set_status(r["status_msg"]);
	
	if( r["ok_fl"] )
	{
	    update_topic_list( r );
	    
	    var n = parseInt(r["topic_count"])
	    
	    if(!isNaN(n) )
	    {
		g_ctx.topic_count = n;
	    }
	    
	    g_ctx.sess_label = r["sess_label"]
	    g_ctx.subject = r["sess_subject"]
	    get_ele('sess_subject_id').value = r["sess_subject"];
	    get_ele('topic_count_id').value = r["topic_count"];
	    get_ele('facts_div').style.display = 'block';
	}
    })
	.catch((error) => {
	    // Handle any errors that occur during the fetch request
	    set_status("A topic generate fetch request error occurred.  " + error);
	});
}

function update_facts_list( factL )
{
    var i = 0;    
    var factListDiv = get_ele("facts_list_div")

    for(i=0; i<factL.length; ++i)
    {
	var f = factL[i]
	
	var div = create_ele("div");
	div.className="fact_div"

	create_para_ele("Title:",div,f.title)
	create_para_ele("Desc:",div,f.description)
	create_para_ele("Full Desc:",div,f.full_description)
	create_para_ele("Background:",div,f.background)
	create_para_ele("Significane:",div,f.significance)
	create_para_ele("Impact:",div,f.impact)
	create_para_ele("Statistics:",div,f.statistics)

	factListDiv.appendChild(div)	    
    }
    
}

function gen_facts()
{
    const formData = {
	sess_label:   g_ctx.sess_label,
	sess_subject: g_ctx.subject
    }

    submit_form("gen_facts",formData).then((r) => {
	set_status(r["status_msg"]);
	
	if( r["ok_fl"] )
	{
	    update_facts_list(r['factL'])
	    get_ele('posts_div').style.display = 'block';
	    
	}
    })
	.catch((error) => {
	    // Handle any errors that occur during the fetch request
	    set_status("A facts generate fetch request error occurred." + error);
	});
}

function update_post_list( postL )
{
    var i = 0;    
    var postListDiv = get_ele("post_list_div")

    for(i=0; i<postL.length; ++i)
    {
	var p = postL[i]
	
	var div = create_ele("div");
	div.className="post_div"

	var check_ele = create_ele("input");
	check_ele.type = "checkbox";
	check_ele.id = "check_" + i;
	check_ele.post_id = p.post_id;
	check_ele.onclick = function(evt){on_check(evt.target.id)}
	
	div.appendChild(check_ele)
	
	create_para_ele("Title:",div,p.title)
	create_para_ele("Writer:",div,p.writer)
	create_para_ele("Post:",div,p.post);
	
	postListDiv.appendChild(div)	    
    }
}

function gen_posts()
{
    const formData = {
	sess_label:   g_ctx.sess_label,
    }

    submit_form("gen_posts",formData).then((r) => {
	set_status(r["status_msg"]);
	
	if( r["ok_fl"] )
	{
	    update_post_list(r['postL'])
	    get_ele('publish_div').style.display = 'block';
	    
	}
    })
	.catch((error) => {
	    // Handle any errors that occur during the fetch request
	    set_status("A facts generate fetch request error occurred." + error);
	});
}

function publish_post()
{
    const formData = {
	sess_label: g_ctx.sess_label,
	post_id: g_ctx.post_id
    }

    submit_form("publish",formData).then((r) => {
	set_status(r["status_msg"]);
	
	if( r["ok_fl"] )
	{
	    // on success
	}
    })
	.catch((error) => {
	    // Handle any errors that occur during the fetch request
	    set_status("A facts generate fetch request error occurred." + error);
	});
    
}

function on_btn_click( btn_id )
{
    switch( btn_id )
    {
	case "facts_btn_id":
	gen_facts()
	break;
	
	case "post_btn_id":
	gen_posts()
	break;

	case "publish_btn_id":
	publish_post()
	break;
    }
}

function on_app_load()
{
    get_ele('facts_div').style.display = 'none';
    get_ele('posts_div').style.display = 'none';
    get_ele('publish_div').style.display = 'none';
    console.log("load")
}

