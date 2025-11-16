from setuptools import setup, find_packages

setup(
    name='vois_ckd',
    version='0.1.0',
    description='An AI-driven diagnostic and prediction system designed to detect Chronic Kidney Disease',
    author='VOIS Team',
    packages=find_packages(),
    install_requires=[
        'Flask==3.0.0',
        'Flask-Login==0.6.3',
        'scikit-learn>=1.5.0',
        'pandas==2.3.3',
        'numpy==2.1.0',
        'joblib==1.3.2',
        'Werkzeug==3.0.1',
        'PyPDF2==3.0.1',
    ],
    entry_points={
        'console_scripts': [
            'vois-ckd=app:main',
        ],
    },
    python_requires='>=3.8',
)