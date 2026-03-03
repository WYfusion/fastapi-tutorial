import React, {useState} from 'react';
import DashboardHeader from "../../components/DashboardHeader";
import {Link, useNavigate} from "react-router-dom";
import FastAPIClient from '../../client';
import config from '../../config';
import Button from '../../components/Button/Button';
import FormInput from '../../components/FormInput/FormInput';

const client = new FastAPIClient(config);

const formatErrorMessage = (detail, fallback) => {
  if (Array.isArray(detail)) {
    const msgs = detail.map((item) => item?.msg).filter(Boolean);
    return msgs.length ? msgs.join('；') : fallback;
  }
  if (detail && typeof detail === 'object') {
    if (detail.msg) return detail.msg;
    return fallback;
  }
  if (typeof detail === 'string' && detail.trim().length) {
    return detail;
  }
  return fallback;
};

const SignUp = () => {
  const [error, setError] = useState({ email: '', password: '', firstName: '' });
  const [submitError, setSubmitError] = useState('');
  const [registerForm, setRegisterForm] = useState({
    email: '',
    password: '',
    firstName: '',
    surname: '',
    isSuperuser: false,
  });

  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()

  const onRegister = (e) => {
    e.preventDefault();
    setLoading(true)
    setError({ email: '', password: '', firstName: '' });
    setSubmitError('');

    if(registerForm.firstName.trim().length <= 0)
    {
      setLoading(false)
      return setError({firstName: "Please Enter First Name"})
    }
    if(registerForm.email.length <= 0)
    {
      setLoading(false)
      return setError({email: "Please Enter Email Address"}) 
    }
    if(registerForm.password.length <= 0)
    {
      setLoading(false)
      return setError({password: "Please Enter Password"})
    }

    client.register(
      registerForm.email,
      registerForm.password,
      registerForm.firstName,
      registerForm.surname,
      registerForm.isSuperuser,
    )
      .then( () => {
        navigate('/login')
      })
      .catch( (err) => {
        setLoading(false)
        const detail = err?.response?.data?.detail;
        const msg = formatErrorMessage(detail, '注册失败，请确认输入信息与后端服务状态');
        setSubmitError(msg);
      });
  }

  return (
      <>
      <section className="bg-black ">
        <DashboardHeader />
        <div className="flex items-center justify-center min-h-screen bg-gray-100 text-left ">
            <div className="w-full max-w-xs m-auto bg-indigo-100 rounded p-5 shadow-lg">  
              <header>
                {/* <img className="w-20 mx-auto mb-5" src="https://img.icons8.com/fluent/344/year-of-tiger.png" /> */}
                <div className="flex items-center justify-center w-20 h-20 mx-auto mb-5 bg-teal-500 rounded-full ">
                <svg className=" h-8 w-8" width="54" height="54" viewBox="0 0 54 54" fill='white'  xmlns="http://www.w3.org/2000/svg" >
                  <path d="M13.5 22.1c1.8-7.2 6.3-10.8 13.5-10.8 10.8 0 12.15 8.1 17.55 9.45 3.6.9 6.75-.45 9.45-4.05-1.8 7.2-6.3 10.8-13.5 10.8-10.8 0-12.15-8.1-17.55-9.45-3.6-.9-6.75.45-9.45 4.05zM0 38.3c1.8-7.2 6.3-10.8 13.5-10.8 10.8 0 12.15 8.1 17.55 9.45 3.6.9 6.75-.45 9.45-4.05-1.8 7.2-6.3 10.8-13.5 10.8-10.8 0-12.15-8.1-17.55-9.45-3.6-.9-6.75.45-9.45 4.05z"/>
                </svg>
                </div>
              </header>
              <form onSubmit={(e) => onRegister(e)}>
                  {submitError ? (
                    <p className="text-red-500 text-sm mb-3">{submitError}</p>
                  ) : null}
                  <FormInput 
                    type={"text"} 
                    name={"firstName"} 
                    label={"First Name"}
                    error={error.firstName} 
                    value={registerForm.firstName} 
                    onChange={(e) => setRegisterForm({...registerForm, firstName: e.target.value })} 
                  />
                  <FormInput 
                    type={"text"} 
                    name={"surname"} 
                    label={"Surname"}
                    value={registerForm.surname} 
                    onChange={(e) => setRegisterForm({...registerForm, surname: e.target.value })} 
                  />
                  <FormInput 
                    type={"email"} 
                    name={"email"} 
                    label={"Email"} 
                    error={error.email}
                    value={registerForm.email} 
                    onChange={(e) => setRegisterForm({...registerForm, email: e.target.value })} 
                  />
                  <FormInput 
                    type={"password"} 
                    name={"password"} 
                    label={"Password"} 
                    error={error.password}
                    value={registerForm.password} 
                    onChange={(e) => setRegisterForm({...registerForm, password: e.target.value })} 
                  />
                  <label className="flex items-center gap-2 mb-6 text-teal-700">
                    <input
                      type="checkbox"
                      checked={registerForm.isSuperuser}
                      onChange={(e) => setRegisterForm({...registerForm, isSuperuser: e.target.checked })}
                    />
                    is_superuser
                  </label>
                <Button title={"Create Account"} error={error.password} loading={loading} />       
              </form>
              
              <footer>
                <Link className="text-teal-700 hover:text-blue-900 text-sm float-right" to="/login">Already Have an account ?</Link>
              </footer> 
            </div>
          </div>
      </section>
    </>
  )
}

export default SignUp;


