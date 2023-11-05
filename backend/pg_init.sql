CREATE SEQUENCE ods_wx_msg_id_seq MINVALUE 1;
CREATE SEQUENCE dwd_wx_dialog_id_seq MINVALUE 1;


CREATE TABLE public.ods_wx_msg (
    id bigint DEFAULT nextval('ods_wx_msg_id_seq'::regclass) NOT NULL,
    sender_name character varying(256)  NOT NULL,
    send_time timestamp without time zone  NOT NULL,
    msg_content text  NOT NULL,
    meta_info text  NOT NULL,
    time_created timestamp with time zone DEFAULT now() NOT NULL,
    time_updated timestamp with time zone DEFAULT now() NOT NULL);
    
  
CREATE TABLE public.dwd_wx_dialog (
    id bigint DEFAULT nextval('dwd_wx_dialog_id_seq'::regclass) NOT NULL,
    msg_id bigint  NOT NULL,
    msg_type character varying(64)  NOT NULL,
    dialog_uuid uuid  NOT NULL,
    dialog_type character varying(64)  NULL,
    extra_info text  NULL,
    time_created timestamp with time zone DEFAULT now() NOT NULL,
    time_updated timestamp with time zone DEFAULT now() NOT NULL);
   
